# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPL-3.0 2016-present Scille SAS
from __future__ import annotations

import math
import unicodedata
from contextlib import asynccontextmanager
from functools import partial
from pathlib import PurePath
from typing import Any, AsyncIterator
from zlib import adler32

import trio
from structlog import get_logger
from winfspy import FileSystem, enable_debug_log
from winfspy.plumbing import FileSystemNotStarted, filetime_now

from parsec._parsec import CoreEvent
from parsec.core.fs.userfs import UserFS
from parsec.core.fs.workspacefs import WorkspaceFS
from parsec.core.mountpoint.exceptions import MountpointDriverCrash, MountpointNoDriveAvailable
from parsec.core.mountpoint.thread_fs_access import ThreadFSAccess
from parsec.core.mountpoint.winfsp_operations import WinFSPOperations, winify_entry_name
from parsec.core.types import EntryID, LocalDevice
from parsec.core.win_registry import parsec_drive_icon_context
from parsec.event_bus import EventBus

__all__ = ("winfsp_mountpoint_runner",)


logger = get_logger()


# The drive letters that parsec can use for mounting workspaces, sorted by priority.
# For instance, if a device has 3 workspaces, they will preferably be mounted on
# `P:\`, `Q:\` and `R:\` respectively. Make sure its length is a prime number so it
# plays well with the algorithm in `sorted_drive_letters`.
DRIVE_LETTERS = "PQRSTUVWXYZHIJKLMNO"
assert len(DRIVE_LETTERS) == 19


def sorted_drive_letters(index: int, length: int, grouping: int = 5) -> str:
    """Sort the drive letters for a specific workspace index, by decreasing priority.

    The first letter should preferably be used. If it's not available, then the second
    letter should be used and so on.

    The number of workspaces (`length`) is also important as this algorithm will round
    it to the next multiple of 5 and use it to group the workspaces together.

    Example with 3 workspaces (rounded to 5 slots)

    | Candidates | W1 | W2 | W3 | XX | XX |
    |------------|----|----|----|----|----|
    | 0          | P  | Q  | R  | S  | T  |
    | 1          | U  | V  | W  | X  | Y  |
    | 2          | Z  | H  | I  | J  | K  |
    | 3          | L  | M  | N  | O  | P  |
    | 4          | Q  | R  | S  | T  | U  |
    | ...

    """
    assert 0 <= index < length
    # Round to the next multiple of grouping, i.e 5
    quotient, remainder = divmod(length, grouping)
    length = (quotient + bool(remainder)) * grouping
    # For the algorithm to work well, the lengths should be coprimes
    assert math.gcd(length, len(DRIVE_LETTERS)) == 1
    # Get all the letters by circling around the drive letter list
    result = ""
    for _ in DRIVE_LETTERS:
        result += DRIVE_LETTERS[index % len(DRIVE_LETTERS)]
        index += length
    return result


async def _get_available_drive(index: int, length: int) -> PurePath:
    drives = (trio.Path(f"{letter}:\\") for letter in sorted_drive_letters(index, length))
    for drive in drives:
        try:
            if not await drive.exists():
                return PurePath(drive)
        # Might fail for some unrelated reasons
        except OSError:
            continue
    # No drive available
    raise MountpointNoDriveAvailable(
        f"None of the following drives are available: {', '.join(DRIVE_LETTERS)}"
    )


def _generate_volume_serial_number(device: LocalDevice, workspace_id: EntryID) -> int:
    return adler32(
        f"{device.organization_id.str}-{device.device_id.str}-{workspace_id.hex}".encode()
    )


async def _wait_for_winfsp_ready(mountpoint_path: PurePath, timeout: float = 1.0) -> None:
    trio_mountpoint_path = trio.Path(mountpoint_path)

    # Polling for `timeout` seconds until winfsp is ready
    with trio.fail_after(timeout):
        while True:
            try:
                if await trio_mountpoint_path.exists():
                    return
                await trio.sleep(0.01)
            # Looks like a revoked workspace has been mounted
            except PermissionError:
                return
            # Might be another OSError like errno 113 (No route to host)
            except OSError:
                return


@asynccontextmanager
async def winfsp_mountpoint_runner(
    user_fs: UserFS,
    workspace_fs: WorkspaceFS,
    base_mountpoint_path: PurePath,
    config: dict[str, Any],
    event_bus: EventBus,
) -> AsyncIterator[PurePath]:
    """
    Raises:
        MountpointDriverCrash
    """
    device = workspace_fs.device
    workspace_name = winify_entry_name(workspace_fs.get_workspace_name())
    trio_token = trio.lowlevel.current_trio_token()
    fs_access = ThreadFSAccess(trio_token, workspace_fs, event_bus)

    user_manifest = user_fs.get_user_manifest()
    workspace_ids = [entry.id for entry in user_manifest.workspaces]
    workspace_index = workspace_ids.index(workspace_fs.workspace_id)
    # `base_mountpoint_path` is ignored given we only mount from a drive
    mountpoint_path = await _get_available_drive(workspace_index, len(workspace_ids))

    # Prepare event information
    event_kwargs = {
        "mountpoint": mountpoint_path,
        "workspace_id": workspace_fs.workspace_id,
        "timestamp": getattr(workspace_fs, "timestamp", None),
    }

    if config.get("debug", False):
        enable_debug_log()

    # Volume label is limited to 32 WCHAR characters, so force the label to
    # ascii to easily enforce the size.
    volume_label = (
        unicodedata.normalize("NFKD", f"{workspace_name.capitalize()}")
        .encode("ascii", "ignore")[:32]
        .decode("ascii")
    )
    volume_serial_number = _generate_volume_serial_number(device, workspace_fs.workspace_id)
    # Types can't be checked when unpacking `event_kwargs`
    operations = WinFSPOperations(fs_access=fs_access, volume_label=volume_label, **event_kwargs)  # type: ignore[arg-type]
    # See https://docs.microsoft.com/en-us/windows/desktop/api/fileapi/nf-fileapi-getvolumeinformationa
    fs = FileSystem(
        mountpoint_path.drive,
        operations,
        sector_size=512,
        sectors_per_allocation_unit=1,
        volume_creation_time=filetime_now(),
        volume_serial_number=volume_serial_number,
        file_info_timeout=1000,
        case_sensitive_search=1,
        case_preserved_names=1,
        unicode_on_disk=1,
        persistent_acls=0,
        reparse_points=0,
        reparse_points_access_check=0,
        named_streams=0,
        read_only_volume=workspace_fs.is_read_only(),
        post_cleanup_when_modified_only=1,
        device_control=0,
        um_file_context_is_user_context2=1,
        file_system_name="Parsec",
        prefix="",
        # The minimum value for IRP timeout is 1 minute (default is 5)
        irp_timeout=60000,
        # security_timeout_valid=1,
        # security_timeout=10000,
    )

    try:
        event_bus.send(CoreEvent.MOUNTPOINT_STARTING, **event_kwargs)

        # Manage drive icon
        drive_letter = mountpoint_path.drive[0]
        with parsec_drive_icon_context(drive_letter, device=user_fs.device):

            # Run fs start in a thread
            await trio.to_thread.run_sync(fs.start)

            # The system is too sensitive right after starting
            await trio.sleep(0.010)  # 10 ms

            # Make sure the mountpoint is ready
            await _wait_for_winfsp_ready(mountpoint_path)

            # Notify the manager that the mountpoint is ready
            yield mountpoint_path

            # Start recording `sharing.updated` events
            with event_bus.waiter_on(CoreEvent.SHARING_UPDATED) as waiter:

                # Loop over `sharing.updated` event
                while True:

                    # Restart the mountpoint with the right read_only flag if necessary
                    # Don't bother with restarting if the workspace has been revoked
                    # It's the manager's responsibility to unmount the workspace in this case
                    if (
                        workspace_fs.is_read_only() != fs.volume_params["read_only_volume"]
                        and not workspace_fs.is_revoked()
                    ):
                        restart = partial(fs.restart, read_only_volume=workspace_fs.is_read_only())
                        await trio.to_thread.run_sync(restart)

                    # Wait and reset waiter
                    await waiter.wait()
                    waiter.clear()

    except Exception as exc:
        raise MountpointDriverCrash(f"WinFSP has crashed on {mountpoint_path}: {exc}") from exc

    finally:
        event_bus.send(CoreEvent.MOUNTPOINT_STOPPING, **event_kwargs)

        # Must run in thread given this call will wait for any winfsp operation
        # to finish so blocking the trio loop can produce a dead lock...
        with trio.CancelScope(shield=True):
            try:
                await trio.to_thread.run_sync(fs.stop)
            # The file system might not be started,
            # if the task gets cancelled before running `fs.start` for instance
            except FileSystemNotStarted:
                pass
