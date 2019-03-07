# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2019 Scille SAS

import os
from pathlib import Path
from contextlib import contextmanager
from sqlite3 import Connection, connect as sqlite_connect

import pendulum

from parsec.core.memory_cache import MemoryCache
from parsec.core.types.access import ManifestAccess
from parsec.crypto import encrypt_raw_with_secret_key, decrypt_raw_with_secret_key


# Alias now
now = pendulum.Pendulum.now

# TODO: shouldn't use core.fs.types.Acces here
# from parsec.core.fs.types import Access
Access = None  # TODO: hack to fix recursive import

# TODO: should be in config.py
DEFAULT_MAX_CACHE_SIZE = 128 * 1024 * 1024
DEFAULT_BLOCK_SIZE = 2 ** 16


class LocalDBError(Exception):
    pass


class LocalDBMissingEntry(LocalDBError):
    def __init__(self, access):
        self.access = access


class LocalDB:
    def __init__(self, path: Path, max_cache_size: int = DEFAULT_MAX_CACHE_SIZE):
        self.memory_cache = MemoryCache()
        self.dirty_conn = None
        self.clean_conn = None
        self._path = Path(path)
        self._clean_db_files = self._path / "clean_data_cache"
        self._dirty_db_files = self._path / "dirty_data_storage"
        self.max_cache_size = max_cache_size
        self.not_written_blocks_size = 0

    @property
    def path(self):
        return str(self._path)

    @property
    def block_limit(self):
        return self.max_cache_size // DEFAULT_BLOCK_SIZE

    # Life cycle

    def connect(self):
        if self.dirty_conn is not None or self.clean_conn is not None:
            raise RuntimeError("Already connected")

        # Create directories
        self._path.mkdir(parents=True, exist_ok=True)
        self._clean_db_files.mkdir(parents=True, exist_ok=True)
        self._dirty_db_files.mkdir(parents=True, exist_ok=True)

        # Connect and initialize database
        self.dirty_conn = sqlite_connect(str(self._path / "dirty_data.sqlite"))
        self.clean_conn = sqlite_connect(str(self._path / "clean_cache.sqlite"))

        # Use auto-commit for dirty data since it is very sensitive
        self.dirty_conn.isolation_level = None

        # Initialize
        self.create_db()

        # Clear invalidated blocks
        with self.open_clean_cursor() as cursor:
            cursor.execute("""DELETE FROM blocks WHERE accessed_on IS NULL""")

    def close(self):
        # Update blocks from memory cache
        if self.clean_conn:
            with self.open_clean_cursor() as cursor:
                for block_id, values in self.memory_cache.clean_blocks.items():
                    cursor.execute(
                        """UPDATE blocks SET accessed_on = ? WHERE block_id = ?""",
                        (values["accessed_on"], block_id),
                    )

        # Idempotency
        if self.dirty_conn is None and self.clean_conn is None:
            return

        # Write changes to the disk and close the connections
        try:
            # Dirty connection uses auto-commit
            # But let's perform a commit anyway, just in case
            self.dirty_conn.commit()
            self.dirty_conn.close()
            self.dirty_conn = None
        finally:
            self.clean_conn.commit()
            self.clean_conn.close()
            self.clean_conn = None

    # Context management

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

    # Cursor management

    @contextmanager
    def _open_cursor(self, conn: Connection):
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def open_dirty_cursor(self):
        return self._open_cursor(self.dirty_conn)

    def open_clean_cursor(self):
        return self._open_cursor(self.clean_conn)

    # Database initialization

    def create_db(self):
        with self.open_dirty_cursor() as dirty_cursor, self.open_clean_cursor() as clean_cursor:

            # User table
            dirty_cursor.execute(
                """CREATE TABLE IF NOT EXISTS users
                    (access_id UUID PRIMARY KEY NOT NULL,
                     blob BYTEA NOT NULL,
                     inserted_on TIMESTAMPTZ);"""
            )

            for cursor in (dirty_cursor, clean_cursor):

                # Manifest tables
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS manifests
                        (manifest_id UUID PRIMARY KEY NOT NULL,
                         blob BYTEA NOT NULL);"""
                )

                # Blocks tables
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS blocks
                        (block_id UUID PRIMARY KEY NOT NULL,
                         size INT NOT NULL,
                         offline BOOLEAN NOT NULL,
                         accessed_on TIMESTAMPTZ,
                         file_path TEXT NOT NULL);"""
                )

    # Size and blocks

    def get_nb_clean_blocks(self):
        with self.open_clean_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM blocks")
            result, = cursor.fetchone()
            return result

    def get_cache_size(self):
        with self.open_clean_cursor() as cursor:
            cursor.execute("SELECT COALESCE(SUM(size), 0) FROM blocks")
            result, = cursor.fetchone()
            return result + self.not_written_blocks_size

    def get_block_cache_size(self):
        cache = str(self._clean_db_files)
        return sum(
            os.path.getsize(os.path.join(cache, f))
            for f in os.listdir(cache)
            if os.path.isfile(os.path.join(cache, f))
        )

    # User operations

    def get_user(self, access: Access):
        user_row = self.memory_cache.get_user(access)
        if not user_row:
            with self.open_dirty_cursor() as cursor:
                cursor.execute(
                    "SELECT access_id, blob, inserted_on FROM users WHERE access_id = ?",
                    (str(access.id),),
                )
                user_row = cursor.fetchone()
            if not user_row or pendulum.parse(user_row[2]).add(hours=1) <= now():
                raise LocalDBMissingEntry(access)
        access_id, blob, created_on = user_row
        return decrypt_raw_with_secret_key(access.key, blob)

    def set_user(self, access: Access, raw: bytes):
        assert isinstance(raw, (bytes, bytearray))
        ciphered = encrypt_raw_with_secret_key(access.key, raw)
        with self.open_dirty_cursor() as cursor:
            cursor.execute(
                """INSERT OR REPLACE INTO users (access_id, blob, inserted_on)
                VALUES (?, ?, ?)""",
                (str(access.id), ciphered, str(now())),
            )
        self.memory_cache.set_user(access, ciphered)

    # Generic manifest operations

    def _check_presence(self, conn: Connection, access: Access):
        with self._open_cursor(conn) as cursor:
            cursor.execute(
                "SELECT manifest_id FROM manifests WHERE manifest_id = ?", (str(access.id),)
            )
            row = cursor.fetchone()
        return bool(row)

    def _get_manifest(self, conn: Connection, access: Access):
        manifest_row = self.memory_cache.get_manifest(conn is self.clean_conn, access)
        if not manifest_row:
            with self._open_cursor(conn) as cursor:
                cursor.execute(
                    "SELECT manifest_id, blob FROM manifests WHERE manifest_id = ?",
                    (str(access.id),),
                )
                manifest_row = cursor.fetchone()
            if not manifest_row:
                raise LocalDBMissingEntry(access)
        manifest_id, blob = manifest_row
        return decrypt_raw_with_secret_key(access.key, blob)

    def _set_manifest(self, conn: Connection, access: Access, raw: bytes):
        assert isinstance(raw, (bytes, bytearray))
        ciphered = encrypt_raw_with_secret_key(access.key, raw)

        with self._open_cursor(conn) as cursor:
            cursor.execute(
                """INSERT OR REPLACE INTO manifests (manifest_id, blob)
                VALUES (?, ?)""",
                (str(access.id), ciphered),
            )
        self.memory_cache.set_manifest(conn is self.clean_conn, access, ciphered)

    def _clear_manifest(self, conn: Connection, access: Access):
        self.memory_cache.clear_manifest(conn is self.clean_conn, access)
        with self._open_cursor(conn) as cursor:
            cursor.execute("DELETE FROM manifests WHERE manifest_id = ?", (str(access.id),))
            cursor.execute("SELECT changes()")
            deleted, = cursor.fetchone()
        if not deleted:
            raise LocalDBMissingEntry(access)

    # Clean manifest operations

    def get_clean_manifest(self, access: Access):
        return self._get_manifest(self.clean_conn, access)

    def set_clean_manifest(self, access: Access, raw: bytes):
        if self._check_presence(self.dirty_conn, access):
            raise ValueError("Cannot set clean manifest: a dirty manifest is already present")
        self._set_manifest(self.clean_conn, access, raw)

    def clear_clean_manifest(self, access: Access):
        self._clear_manifest(self.clean_conn, access)

    # Dirty manifest operations

    def get_dirty_manifest(self, access: Access):
        return self._get_manifest(self.dirty_conn, access)

    def set_dirty_manifest(self, access: Access, raw: bytes):
        if self._check_presence(self.clean_conn, access):
            raise ValueError("Cannot set dirty manifest: a clean manifest is already present")
        self._set_manifest(self.dirty_conn, access, raw)

    def clear_dirty_manifest(self, access: Access):
        self._clear_manifest(self.dirty_conn, access)

    # Generic block operations

    def _update_block_accessed_on(self, conn: Connection, access: Access, accessed_on):
        with self._open_cursor(conn) as cursor:
            cursor.execute(
                """UPDATE blocks SET accessed_on = ? WHERE block_id = ?""",
                (accessed_on, str(access.id)),
            )
            cursor.execute("SELECT changes()")
            changes, = cursor.fetchone()

        if not changes:
            raise LocalDBMissingEntry(access)

    def _get_block(self, conn: Connection, path: Path, access: Access):
        accessed_on = None if (conn is self.clean_conn) else str(now())
        block_row = self.memory_cache.get_block(conn is self.clean_conn, access)
        if block_row:
            ciphered = block_row[2]
        else:
            ciphered = self._read_file(access, path)
            purged_block = self.memory_cache.set_block(conn is self.clean_conn, access, ciphered)
            if purged_block:
                self._update_block_accessed_on(conn, purged_block[0], purged_block[1])
            self._update_block_accessed_on(conn, access, accessed_on)

        return decrypt_raw_with_secret_key(access.key, ciphered)

    def _set_block(self, conn: Connection, path: Path, access: Access, raw: bytes):
        assert isinstance(raw, (bytes, bytearray))
        filepath = path / str(access.id)
        ciphered = encrypt_raw_with_secret_key(access.key, raw)

        # Update database
        if conn is self.dirty_conn:
            with self._open_cursor(conn) as cursor:
                cursor.execute(
                    """INSERT OR REPLACE INTO
                    blocks (block_id, size, offline, accessed_on, file_path)
                    VALUES (?, ?, ?, ?, ?)""",
                    (str(access.id), len(ciphered), False, str(now()), str(filepath)),
                )
        else:
            self.not_written_blocks_size += len(ciphered)
        purged_block = self.memory_cache.set_block(conn is self.clean_conn, access, ciphered)
        if purged_block:
            self._update_block_accessed_on(conn, purged_block[0], purged_block[1])

        # Write file
        self._write_file(access, ciphered, path)

    def _clear_block(self, conn: Connection, path: Path, access: Access):
        with self._open_cursor(conn) as cursor:
            self.memory_cache.get_block(conn is self.clean_conn, access)
            cursor.execute(
                "SELECT accessed_on, size from blocks WHERE block_id = ?", (str(access.id),)
            )
            row = cursor.fetchone()
            if row and not row[0]:
                self.not_written_blocks_size -= len(row[1])
            cursor.execute("DELETE FROM blocks WHERE block_id = ?", (str(access.id),))
            cursor.execute("SELECT changes()")
            changes, = cursor.fetchone()

        cached = self.memory_cache.clear_block(conn is self.clean_conn, access)
        if not changes and not cached:
            raise LocalDBMissingEntry(access)

        self._remove_file(access, path)

    # Clean block operations

    def get_clean_block(self, access: Access):
        return self._get_block(self.clean_conn, self._clean_db_files, access)

    def set_clean_block(self, access: Access, raw: bytes):
        self._set_block(self.clean_conn, self._clean_db_files, access, raw)

        # Clean up if necessary
        limit = self.get_nb_clean_blocks() - self.block_limit
        if limit > 0:
            self.clear_clean_blocks(limit=limit)

    def clear_clean_block(self, access):
        self._clear_block(self.clean_conn, self._clean_db_files, access)

    # Dirty block operations

    def get_dirty_block(self, access: Access):
        return self._get_block(self.dirty_conn, self._dirty_db_files, access)

    def set_dirty_block(self, access: Access, raw: bytes):
        self._set_block(self.dirty_conn, self._dirty_db_files, access, raw)

    def clear_dirty_block(self, access):
        self._clear_block(self.dirty_conn, self._dirty_db_files, access)

    # Block file operations

    def _read_file(self, access: Access, path: Path):
        filepath = path / str(access.id)
        try:
            return filepath.read_bytes()
        except FileNotFoundError:
            raise LocalDBMissingEntry(access)

    def _write_file(self, access: Access, content: bytes, path: Path):
        filepath = path / str(access.id)
        filepath.write_bytes(content)

    def _remove_file(self, access: Access, path: Path):
        filepath = path / str(access.id)
        try:
            filepath.unlink()
        except FileNotFoundError:
            raise LocalDBMissingEntry(access)

    # Garbage collection

    def clear_clean_blocks(self, limit=None):
        limit_string = f" LIMIT {limit}" if limit is not None else ""

        with self.open_clean_cursor() as cursor:
            cursor.execute(
                """
                SELECT block_id FROM blocks ORDER BY accessed_on ASC
                """
                + limit_string
            )
            block_ids = [block_id for (block_id,) in cursor.fetchall()]

        for block_id in block_ids:
            self.clear_clean_block(ManifestAccess(block_id))

    def run_block_garbage_collector(self):
        self.clear_clean_blocks()
