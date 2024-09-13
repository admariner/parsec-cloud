# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

from typing import Optional

from .addr import ParsecOrganizationAddr
from .common import (
    U64,
    DateTime,
    DeviceID,
    DeviceLabel,
    EntryName,
    ErrorVariant,
    Handle,
    HumanHandle,
    OrganizationID,
    Password,
    Path,
    Result,
    Structure,
    UserID,
    UserProfile,
    Variant,
    VariantItemTuple,
    VariantItemUnit,
    VlobID,
    RealmRole,
    Ref,
)
from .invite import DeviceSaveStrategy
from .config import ClientConfig
from .events import OnClientEventCallback


class WaitForDeviceAvailableError(ErrorVariant):
    class Internal:
        pass


async def wait_for_device_available(
    config_dir: Ref[Path],
    device_id: DeviceID,
) -> Result[None, WaitForDeviceAvailableError]:
    raise NotImplementedError


class DeviceAccessStrategy(Variant):
    class Keyring:
        key_file: Path

    class Password:
        password: Password
        key_file: Path

    class Smartcard:
        key_file: Path


class ClientStartError(ErrorVariant):
    class DeviceUsedByAnotherProcess:
        pass

    class LoadDeviceInvalidPath:
        pass

    class LoadDeviceInvalidData:
        pass

    class LoadDeviceDecryptionFailed:
        pass

    class Internal:
        pass


async def client_start(
    config: ClientConfig,
    on_event_callback: OnClientEventCallback,
    access: DeviceAccessStrategy,
) -> Result[Handle, ClientStartError]:
    raise NotImplementedError


class ClientStopError(ErrorVariant):
    class Internal:
        pass


async def client_stop(client: Handle) -> Result[None, ClientStopError]:
    raise NotImplementedError


class ClientInfoError(ErrorVariant):
    class Stopped:
        pass

    class Internal:
        pass


class ActiveUsersLimit(Variant):
    LimitedTo = VariantItemTuple(U64)
    NoLimit = VariantItemUnit


class ServerConfig(Structure):
    user_profile_outsider_allowed: bool
    active_users_limit: ActiveUsersLimit


class ClientInfo(Structure):
    organization_addr: ParsecOrganizationAddr
    organization_id: OrganizationID
    device_id: DeviceID
    user_id: UserID
    device_label: DeviceLabel
    human_handle: HumanHandle
    current_profile: UserProfile
    server_config: ServerConfig


async def client_info(
    client: Handle,
) -> Result[ClientInfo, ClientInfoError]:
    raise NotImplementedError


class ClientChangeAuthenticationError(ErrorVariant):
    class InvalidPath:
        pass

    class InvalidData:
        pass

    class DecryptionFailed:
        pass

    class Internal:
        pass


async def client_change_authentication(
    client_config: ClientConfig,
    current_auth: DeviceAccessStrategy,
    new_auth: DeviceSaveStrategy,
) -> Result[None, ClientChangeAuthenticationError]:
    raise NotImplementedError


class UserInfo(Structure):
    id: UserID
    human_handle: HumanHandle
    current_profile: UserProfile
    created_on: DateTime
    created_by: Optional[DeviceID]
    revoked_on: Optional[DateTime]
    revoked_by: Optional[DeviceID]


class DeviceInfo(Structure):
    id: DeviceID
    device_label: DeviceLabel
    created_on: DateTime
    created_by: Optional[DeviceID]


class ClientRevokeUserError(ErrorVariant):
    class Stopped:
        pass

    class Offline:
        pass

    class UserIsSelf:
        pass

    class UserNotFound:
        pass

    class AuthorNotAllowed:
        pass

    class TimestampOutOfBallpark:
        pass

    class NoKey:
        pass

    class InvalidKeysBundle:
        pass

    class InvalidCertificate:
        pass

    class Internal:
        pass


async def client_revoke_user(
    client: Handle,
    user: UserID,
) -> Result[None, ClientRevokeUserError]:
    raise NotImplementedError


class ClientListUsersError(ErrorVariant):
    class Stopped:
        pass

    class Internal:
        pass


async def client_list_users(
    client: Handle,
    skip_revoked: bool,
    # offset: Optional[int],
    # limit: Optional[int],
) -> Result[list[UserInfo], ClientListUsersError]:
    raise NotImplementedError


class ClientListUserDevicesError(ErrorVariant):
    class Stopped:
        pass

    class Internal:
        pass


async def client_list_user_devices(
    client: Handle,
    user: UserID,
) -> Result[list[DeviceInfo], ClientListUserDevicesError]:
    raise NotImplementedError


class ClientGetUserDeviceError(ErrorVariant):
    class Stopped:
        pass

    class NonExisting:
        pass

    class Internal:
        pass


async def client_get_user_device(
    client: Handle,
    device: DeviceID,
) -> Result[tuple[UserInfo, DeviceInfo], ClientGetUserDeviceError]:
    raise NotImplementedError


class WorkspaceUserAccessInfo(Structure):
    user_id: UserID
    human_handle: HumanHandle
    current_profile: UserProfile
    current_role: RealmRole


class ClientListWorkspaceUsersError(ErrorVariant):
    class Stopped:
        pass

    class Internal:
        pass


async def client_list_workspace_users(
    client: Handle,
    realm_id: VlobID,
) -> Result[list[WorkspaceUserAccessInfo], ClientListWorkspaceUsersError]:
    raise NotImplementedError


class ClientListWorkspacesError(ErrorVariant):
    class Internal:
        pass


class WorkspaceInfo(Structure):
    id: VlobID
    current_name: EntryName
    current_self_role: RealmRole
    is_started: bool
    is_bootstrapped: bool


async def client_list_workspaces(
    client: Handle,
) -> Result[list[WorkspaceInfo], ClientListWorkspacesError]:
    raise NotImplementedError


class ClientCreateWorkspaceError(ErrorVariant):
    class Stopped:
        pass

    class Internal:
        pass


async def client_create_workspace(
    client: Handle,
    name: EntryName,
) -> Result[VlobID, ClientCreateWorkspaceError]:
    raise NotImplementedError


class ClientRenameWorkspaceError(ErrorVariant):
    class WorkspaceNotFound:
        pass

    class AuthorNotAllowed:
        pass

    class Offline:
        pass

    class Stopped:
        pass

    class TimestampOutOfBallpark:
        server_timestamp: DateTime
        client_timestamp: DateTime
        ballpark_client_early_offset: float
        ballpark_client_late_offset: float

    class NoKey:
        pass

    class InvalidKeysBundle:
        pass

    class InvalidCertificate:
        pass

    class InvalidEncryptedRealmName:
        pass

    class Internal:
        pass


async def client_rename_workspace(
    client: Handle,
    realm_id: VlobID,
    new_name: EntryName,
) -> Result[None, ClientRenameWorkspaceError]:
    raise NotImplementedError


class ClientShareWorkspaceError(ErrorVariant):
    class Stopped:
        pass

    class RecipientIsSelf:
        pass

    class RecipientNotFound:
        pass

    class WorkspaceNotFound:
        pass

    class RecipientRevoked:
        pass

    class AuthorNotAllowed:
        pass

    class RoleIncompatibleWithOutsider:
        pass

    class Offline:
        pass

    class TimestampOutOfBallpark:
        server_timestamp: DateTime
        client_timestamp: DateTime
        ballpark_client_early_offset: float
        ballpark_client_late_offset: float

    class InvalidKeysBundle:
        pass

    class InvalidCertificate:
        pass

    class Internal:
        pass


async def client_share_workspace(
    client: Handle,
    realm_id: VlobID,
    recipient: UserID,
    role: Optional[RealmRole],
) -> Result[None, ClientShareWorkspaceError]:
    raise NotImplementedError


def is_keyring_available() -> bool:
    raise NotImplementedError
