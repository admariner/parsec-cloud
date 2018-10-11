import triopg
import logbook
from uuid import UUID

from parsec.utils import ejson_dumps, ejson_loads


logger = logbook.Logger("parsec.backend.driver")


async def init_db(url, force=False):
    conn = await triopg.connect(url)
    async with conn.transaction():

        if force:
            # TODO: Ideally we would totally drop the db here instead of just
            # the databases we know...
            await conn.execute(
                """
                DROP TABLE IF EXISTS
                    users,
                    devices,

                    user_invitations,
                    unconfigured_devices,
                    device_configuration_tries,

                    messages,
                    vlobs,
                    beacons,

                    blockstore
                CASCADE;

                DROP TYPE IF EXISTS
                    USER_INVITATION_STATUS,
                    DEVICE_INVITATION_STATUS,
                    DEVICE_CONF_TRY_STATUS
                CASCADE;
                """
            )
        else:
            # TODO: not a really elegant way to determine if the database
            # is already initialized...
            db_initialized = await conn.execute(
                """
                SELECT exists (
                    SELECT 1 FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'users'
                )
            """
            )
            if db_initialized:
                return

        await conn.execute(
            """
            CREATE TABLE users (
                user_id VARCHAR(32) PRIMARY KEY,
                created_on TIMESTAMP NOT NULL,
                broadcast_key BYTEA NOT NULL
            );

            CREATE TABLE devices (
                device_id VARCHAR(65) PRIMARY KEY,
                device_name VARCHAR(32),
                user_id VARCHAR(32) REFERENCES users (user_id) NOT NULL,
                created_on TIMESTAMP NOT NULL,
                verify_key BYTEA NOT NULL,
                revocated_on TIMESTAMP,
                UNIQUE (user_id, device_id)
            );
            """
        )

        await conn.execute(
            """
            CREATE TYPE USER_INVITATION_STATUS AS ENUM ('pending', 'claimed', 'rejected');
            CREATE TABLE user_invitations (
                _id SERIAL PRIMARY KEY,
                status USER_INVITATION_STATUS NOT NULL,
                user_id VARCHAR(32) NOT NULL,
                invited_on TIMESTAMP NOT NULL,
                invitation_token TEXT NOT NULL,
                claim_tries INTEGER NOT NULL,
                claimed_on TIMESTAMP
            )"""
        )

        await conn.execute(
            """
            CREATE TABLE unconfigured_devices (
                _id SERIAL PRIMARY KEY,
                user_id VARCHAR(32) REFERENCES users (user_id) NOT NULL,
                device_name VARCHAR(32) NOT NULL,
                created_on TIMESTAMP NOT NULL,
                configure_token TEXT NOT NULL,
                UNIQUE(user_id, device_name)
            )"""
        )

        await conn.execute(
            """
            CREATE TYPE DEVICE_CONF_TRY_STATUS AS ENUM ('waiting_answer', 'accepted', 'refused');
            CREATE TABLE device_configuration_tries (
                config_try_id VARCHAR(32) PRIMARY KEY,
                user_id VARCHAR(32) REFERENCES users (user_id) NOT NULL,
                status DEVICE_CONF_TRY_STATUS NOT NULL,
                refused_reason TEXT,
                device_name VARCHAR(32) NOT NULL,
                device_verify_key BYTEA NOT NULL,
                exchange_cipherkey BYTEA NOT NULL,
                salt BYTEA NOT NULL,
                ciphered_user_privkey BYTEA,
                ciphered_user_manifest_access BYTEA,
                UNIQUE(user_id, config_try_id)
            )"""
        )

        await conn.execute(
            """
            CREATE TABLE messages (
                _id SERIAL PRIMARY KEY,
                recipient VARCHAR(32) REFERENCES users (user_id) NOT NULL,
                sender VARCHAR(65) REFERENCES devices (device_id) NOT NULL,
                body BYTEA NOT NULL
            )"""
        )

        await conn.execute(
            """
            CREATE TABLE vlobs (
                _id SERIAL PRIMARY KEY,
                vlob_id UUID NOT NULL,
                version INTEGER NOT NULL,
                rts TEXT NOT NULL,
                wts TEXT NOT NULL,
                blob BYTEA NOT NULL,
                UNIQUE(vlob_id, version)
            )"""
        )

        await conn.execute(
            """
            CREATE TABLE beacons (
                _id SERIAL PRIMARY KEY,
                beacon_id UUID NOT NULL,
                beacon_index INTEGER NOT NULL,
                src_id UUID NOT NULL,
                -- src_id UUID REFERENCES vlobs (vlob_id) NOT NULL,
                src_version INTEGER NOT NULL
            )"""
        )

        await conn.execute(
            """
            CREATE TABLE blockstore (
                _id SERIAL PRIMARY KEY,
                block_id UUID UNIQUE NOT NULL,
                block BYTEA NOT NULL
            )"""
        )


class PGHandler:
    def __init__(self, url, event_bus):
        self.url = url
        self.event_bus = event_bus
        self.pool = None

    async def init(self, nursery):
        await init_db(self.url)

        self.pool = await triopg.create_pool(self.url)
        # This connection is dedicated to the notifications listening, so it
        # would only complicate stuff to include it into the connection pool
        self.notification_conn = await triopg.connect(self.url)

        await self.notification_conn.add_listener("app_notification", self._on_notification)

    def _on_notification(self, connection, pid, channel, payload):
        data = ejson_loads(payload)
        signal = data.pop("__signal__")
        if signal == "beacon.updated":
            data["beacon_id"] = UUID(data["beacon_id"])
            data["src_id"] = UUID(data["src_id"])
        logger.debug("notif received {}, {}, {}", pid, channel, payload)
        self.event_bus.send(signal, **data)

    async def teardown(self):
        await self.notification_conn.close()
        await self.pool.close()

    async def ping(self, author, ping):
        async with self.pool.acquire() as conn:
            await send_signal(conn, "pinged", author=author, ping=ping)


async def send_signal(conn, signal, **kwargs):
    raw_data = ejson_dumps({"__signal__": signal, **kwargs})
    await conn.execute("SELECT pg_notify($1, $2)", "app_notification", raw_data)
    logger.debug("notif sent {}", raw_data)
