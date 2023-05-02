# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPL-3.0 2016-present Scille SAS

from __future__ import annotations

from parsec._parsec_pyi import (
    BackendConnectionError,
    BackendConnectionRefused,
    BackendInvitationAlreadyUsed,
    BackendInvitationNotFound,
    BackendInvitationOnExistingMember,
    BackendNotAvailable,
    BackendNotFoundError,
    BackendOutOfBallparkError,
    BackendProtocolError,
    DataError,
    EntryNameError,
    InviteActiveUsersLimitReachedError,
    InviteAlreadyUsedError,
    InviteError,
    InviteNotFoundError,
    InvitePeerResetError,
    PkiEnrollmentError,
    PkiEnrollmentLocalPendingCannotReadError,
    PkiEnrollmentLocalPendingCannotRemoveError,
    PkiEnrollmentLocalPendingCannotSaveError,
    PkiEnrollmentLocalPendingError,
    PkiEnrollmentLocalPendingValidationError,
)
from parsec._parsec_pyi.addrs import (
    BackendActionAddr,
    BackendAddr,
    BackendInvitationAddr,
    BackendOrganizationAddr,
    BackendOrganizationBootstrapAddr,
    BackendOrganizationFileLinkAddr,
    BackendPkiEnrollmentAddr,
    export_root_verify_key,
)
from parsec._parsec_pyi.backend_connection import AnonymousCmds, AuthenticatedCmds, InvitedCmds
from parsec._parsec_pyi.backend_events import (
    BackendEvent,
    BackendEventInviteConduitUpdated,
    BackendEventInviteStatusChanged,
    BackendEventMessageReceived,
    BackendEventOrganizationExpired,
    BackendEventPinged,
    BackendEventPkiEnrollmentUpdated,
    BackendEventRealmMaintenanceFinished,
    BackendEventRealmMaintenanceStarted,
    BackendEventRealmRolesUpdated,
    BackendEventRealmVlobsUpdated,
    BackendEventUserRevoked,
)
from parsec._parsec_pyi.certif import (
    DeviceCertificate,
    RealmRoleCertificate,
    RevokedUserCertificate,
    SequesterAuthorityCertificate,
    SequesterServiceCertificate,
    UserCertificate,
)
from parsec._parsec_pyi.core_fs import ChangesAfterSync, UserRemoteLoader
from parsec._parsec_pyi.crypto import (
    CryptoError,
    HashDigest,
    PrivateKey,
    PublicKey,
    SecretKey,
    SequesterPrivateKeyDer,
    SequesterPublicKeyDer,
    SequesterSigningKeyDer,
    SequesterVerifyKeyDer,
    SigningKey,
    VerifyKey,
    generate_nonce,
)
from parsec._parsec_pyi.device import DeviceFileType
from parsec._parsec_pyi.device_file import DeviceFile
from parsec._parsec_pyi.enumerate import (
    InvitationStatus,
    InvitationType,
    RealmRole,
    UserProfile,
)
from parsec._parsec_pyi.events import CoreEvent
from parsec._parsec_pyi.file_operation import (
    prepare_read,
    prepare_reshape,
    prepare_resize,
    prepare_write,
)
from parsec._parsec_pyi.ids import (
    BlockID,
    ChunkID,
    DeviceID,
    DeviceLabel,
    DeviceName,
    EnrollmentID,
    EntryID,
    HumanHandle,
    InvitationToken,
    OrganizationID,
    RealmID,
    SequesterServiceID,
    UserID,
    VlobID,
)
from parsec._parsec_pyi.invite import (
    DeviceClaimInitialCtx,
    DeviceClaimInProgress1Ctx,
    DeviceClaimInProgress2Ctx,
    DeviceClaimInProgress3Ctx,
    DeviceGreetInitialCtx,
    DeviceGreetInProgress1Ctx,
    DeviceGreetInProgress2Ctx,
    DeviceGreetInProgress3Ctx,
    DeviceGreetInProgress4Ctx,
    InviteDeviceConfirmation,
    InviteDeviceData,
    InviteUserConfirmation,
    InviteUserData,
    SASCode,
    UserClaimInitialCtx,
    UserClaimInProgress1Ctx,
    UserClaimInProgress2Ctx,
    UserClaimInProgress3Ctx,
    UserGreetInitialCtx,
    UserGreetInProgress1Ctx,
    UserGreetInProgress2Ctx,
    UserGreetInProgress3Ctx,
    UserGreetInProgress4Ctx,
    claimer_retrieve_info,
    generate_sas_code_candidates,
    generate_sas_codes,
)
from parsec._parsec_pyi.local_device import (
    AvailableDevice,
    DeviceInfo,
    LocalDevice,
    LocalDeviceAlreadyExistsError,
    LocalDeviceCryptoError,
    LocalDeviceError,
    LocalDeviceNotFoundError,
    LocalDevicePackingError,
    LocalDeviceValidationError,
    UserInfo,
    change_device_password,
    get_available_device,
    list_available_devices,
    load_recovery_device,
    save_device_with_password,
    save_device_with_password_in_config,
    save_recovery_device,
)
from parsec._parsec_pyi.local_manifest import (
    Chunk,
    LocalFileManifest,
    LocalFolderManifest,
    LocalUserManifest,
    LocalWorkspaceManifest,
    local_manifest_decrypt_and_load,
)
from parsec._parsec_pyi.manifest import (
    AnyRemoteManifest,
    BlockAccess,
    EntryName,
    FileManifest,
    FolderManifest,
    UserManifest,
    WorkspaceEntry,
    WorkspaceManifest,
    manifest_decrypt_and_load,
    manifest_decrypt_verify_and_load,
    manifest_unverified_load,
    manifest_verify_and_load,
)
from parsec._parsec_pyi.message import (
    MessageContent,
    PingMessageContent,
    SharingGrantedMessageContent,
    SharingReencryptedMessageContent,
    SharingRevokedMessageContent,
)
from parsec._parsec_pyi.misc import ApiVersion
from parsec._parsec_pyi.organization import OrganizationConfig, OrganizationStats
from parsec._parsec_pyi.pki import (
    LocalPendingEnrollment,
    PkiEnrollmentAnswerPayload,
    PkiEnrollmentSubmitPayload,
    X509Certificate,
)
from parsec._parsec_pyi.protocol import (
    ActiveUsersLimit,
    ProtocolError,
    ProtocolErrorFields,
    ReencryptionBatchEntry,
    anonymous_cmds,
    authenticated_cmds,
    invited_cmds,
)
from parsec._parsec_pyi.regex import Regex
from parsec._parsec_pyi.remote_devices_manager import (
    RemoteDevicesManager,
    RemoteDevicesManagerBackendOfflineError,
    RemoteDevicesManagerDeviceNotFoundError,
    RemoteDevicesManagerError,
    RemoteDevicesManagerInvalidTrustchainError,
    RemoteDevicesManagerNotFoundError,
    RemoteDevicesManagerUserNotFoundError,
)
from parsec._parsec_pyi.storage.user_storage import UserStorage, user_storage_non_speculative_init
from parsec._parsec_pyi.storage.workspace_storage import (
    PseudoFileDescriptor,
    WorkspaceStorage,
    WorkspaceStorageSnapshot,
    workspace_storage_non_speculative_init,
)
from parsec._parsec_pyi.time import DateTime, LocalDateTime, TimeProvider, mock_time
from parsec._parsec_pyi.trustchain import (
    TrustchainContext,
    TrustchainError,
    TrustchainErrorException,
)
from parsec._parsec_pyi.user import UsersPerProfileDetailItem

__all__ = [
    "ApiVersion",
    # Command Error
    "BackendConnectionError",
    "BackendProtocolError",
    "BackendNotAvailable",
    "BackendConnectionRefused",
    "BackendInvitationAlreadyUsed",
    "BackendInvitationNotFound",
    "BackendNotFoundError",
    "BackendInvitationOnExistingMember",
    "BackendOutOfBallparkError",
    # Data Error
    "DataError",
    "EntryNameError",
    "PkiEnrollmentError",
    "PkiEnrollmentLocalPendingError",
    "PkiEnrollmentLocalPendingCannotReadError",
    "PkiEnrollmentLocalPendingCannotRemoveError",
    "PkiEnrollmentLocalPendingCannotSaveError",
    "PkiEnrollmentLocalPendingValidationError",
    # Invite Error
    "InviteActiveUsersLimitReachedError",
    "InviteAlreadyUsedError",
    "InviteError",
    "InviteNotFoundError",
    "InvitePeerResetError",
    # Certif
    "UserCertificate",
    "DeviceCertificate",
    "RevokedUserCertificate",
    "RealmRoleCertificate",
    "SequesterAuthorityCertificate",
    "SequesterServiceCertificate",
    # Device
    "DeviceFileType",
    # CoreFs
    "ChangesAfterSync",
    "UserRemoteLoader",
    # Crypto
    "SecretKey",
    "HashDigest",
    "SigningKey",
    "VerifyKey",
    "PrivateKey",
    "PublicKey",
    "SequesterPrivateKeyDer",
    "SequesterPublicKeyDer",
    "SequesterSigningKeyDer",
    "SequesterVerifyKeyDer",
    "generate_nonce",
    "CryptoError",
    # DeviceFile
    "DeviceFile",
    # Enumerate
    "InvitationType",
    "InvitationStatus",
    "InvitationType",
    "RealmRole",
    "UserProfile",
    "CoreEvent",
    # Ids
    "OrganizationID",
    "EntryID",
    "BlockID",
    "VlobID",
    "ChunkID",
    "HumanHandle",
    "DeviceLabel",
    "DeviceID",
    "DeviceName",
    "UserID",
    "RealmID",
    "SequesterServiceID",
    "EnrollmentID",
    "InvitationToken",
    # Invite
    "SASCode",
    "generate_sas_code_candidates",
    "generate_sas_codes",
    "InviteUserConfirmation",
    "InviteDeviceData",
    "InviteDeviceConfirmation",
    "InviteUserData",
    # Invite Greeter
    "UserGreetInitialCtx",
    "DeviceGreetInitialCtx",
    "UserGreetInProgress1Ctx",
    "DeviceGreetInProgress1Ctx",
    "UserGreetInProgress2Ctx",
    "DeviceGreetInProgress2Ctx",
    "UserGreetInProgress3Ctx",
    "DeviceGreetInProgress3Ctx",
    "UserGreetInProgress4Ctx",
    "DeviceGreetInProgress4Ctx",
    # Invite Claimer
    "DeviceClaimInitialCtx",
    "DeviceClaimInProgress1Ctx",
    "DeviceClaimInProgress2Ctx",
    "DeviceClaimInProgress3Ctx",
    "UserClaimInitialCtx",
    "UserClaimInProgress1Ctx",
    "UserClaimInProgress2Ctx",
    "UserClaimInProgress3Ctx",
    "claimer_retrieve_info",
    # Addrs
    "BackendAddr",
    "BackendActionAddr",
    "BackendInvitationAddr",
    "BackendOrganizationAddr",
    "BackendOrganizationBootstrapAddr",
    "BackendOrganizationFileLinkAddr",
    "BackendPkiEnrollmentAddr",
    "export_root_verify_key",
    # Backend connection
    "AnonymousCmds",
    "AuthenticatedCmds",
    "InvitedCmds",
    "UserClaimInitialCtx",
    "UserClaimInProgress1Ctx",
    "UserClaimInProgress2Ctx",
    "UserClaimInProgress3Ctx",
    "DeviceClaimInitialCtx",
    "DeviceClaimInProgress1Ctx",
    "DeviceClaimInProgress2Ctx",
    "DeviceClaimInProgress3Ctx",
    "claimer_retrieve_info",
    # Backend internal events
    "BackendEvent",
    "BackendEventInviteConduitUpdated",
    "BackendEventUserRevoked",
    "BackendEventOrganizationExpired",
    "BackendEventPinged",
    "BackendEventMessageReceived",
    "BackendEventInviteStatusChanged",
    "BackendEventRealmMaintenanceFinished",
    "BackendEventRealmMaintenanceStarted",
    "BackendEventRealmVlobsUpdated",
    "BackendEventRealmRolesUpdated",
    "BackendEventPkiEnrollmentUpdated",
    # Local Manifest
    "Chunk",
    "LocalFileManifest",
    "LocalFolderManifest",
    "LocalUserManifest",
    "LocalWorkspaceManifest",
    "local_manifest_decrypt_and_load",
    # Manifest
    "EntryName",
    "WorkspaceEntry",
    "BlockAccess",
    "FolderManifest",
    "FileManifest",
    "WorkspaceManifest",
    "UserManifest",
    "AnyRemoteManifest",
    "manifest_decrypt_and_load",
    "manifest_decrypt_verify_and_load",
    "manifest_verify_and_load",
    "manifest_unverified_load",
    # Message
    "MessageContent",
    "SharingGrantedMessageContent",
    "SharingReencryptedMessageContent",
    "SharingRevokedMessageContent",
    "PingMessageContent",
    # Organization
    "OrganizationConfig",
    "OrganizationStats",
    # Pki
    "PkiEnrollmentAnswerPayload",
    "PkiEnrollmentSubmitPayload",
    "X509Certificate",
    "LocalPendingEnrollment",
    # User
    "UsersPerProfileDetailItem",
    # Time
    "DateTime",
    "LocalDateTime",
    "TimeProvider",
    "mock_time",
    # Trustchain
    "TrustchainContext",
    "TrustchainError",
    "TrustchainErrorException",
    # Local Device
    "AvailableDevice",
    "DeviceInfo",
    "LocalDevice",
    "LocalDeviceError",
    "LocalDeviceCryptoError",
    "LocalDeviceValidationError",
    "LocalDeviceAlreadyExistsError",
    "LocalDevicePackingError",
    "LocalDeviceNotFoundError",
    "UserInfo",
    "change_device_password",
    "get_available_device",
    "list_available_devices",
    "load_recovery_device",
    "save_device_with_password",
    "save_device_with_password_in_config",
    # Workspace Storage
    "WorkspaceStorage",
    "WorkspaceStorageSnapshot",
    "PseudoFileDescriptor",
    "workspace_storage_non_speculative_init",
    # User Storage
    "UserStorage",
    "user_storage_non_speculative_init",
    "save_recovery_device",
    # File Operations
    "prepare_read",
    "prepare_reshape",
    "prepare_resize",
    "prepare_write",
    # Protocol Cmd
    "authenticated_cmds",
    "anonymous_cmds",
    "invited_cmds",
    "ProtocolError",
    "ProtocolErrorFields",
    "ReencryptionBatchEntry",
    "ActiveUsersLimit",
    # RemoteDevicesManager
    "RemoteDevicesManager",
    "RemoteDevicesManagerBackendOfflineError",
    "RemoteDevicesManagerDeviceNotFoundError",
    "RemoteDevicesManagerError",
    "RemoteDevicesManagerInvalidTrustchainError",
    "RemoteDevicesManagerNotFoundError",
    "RemoteDevicesManagerUserNotFoundError",
    # Regex
    "Regex",
]
