# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS
from __future__ import annotations

from abc import ABC
from base64 import b64encode
from typing import TYPE_CHECKING, Annotated, Literal, override
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, PlainValidator

from parsec._parsec import (
    ActiveUsersLimit,
    DateTime,
    DeviceID,
    EnrollmentID,
    InvitationStatus,
    InvitationToken,
    OrganizationID,
    RealmRole,
    UserID,
    UserProfile,
    VlobID,
    authenticated_cmds,
)

if TYPE_CHECKING:
    from parsec.components.events import RegisteredClient


# PostgreSQL only allows up to 8000 bytes for the payload of a NOTIFY so not all blob
# can be passed with the event (on top of that we keep the events in cache for SSE
# last-event-id, so better avoid too much pressure of the RAM)
# We keep a large margin with PostgreSQL limit given the event also contains additional
# fields and must be encoded in base64 (which alone adds ~33% in size).
EVENT_VLOB_MAX_BLOB_SIZE = 4096


OrganizationIDField = Annotated[
    OrganizationID,
    PlainValidator(lambda x: x if isinstance(x, OrganizationID) else OrganizationID(x)),
    PlainSerializer(lambda x: x.str, return_type=str),
]
UserIDField = Annotated[
    UserID,
    PlainValidator(lambda x: x if isinstance(x, UserID) else UserID(x)),
    PlainSerializer(lambda x: x.str, return_type=str),
]
DeviceIDField = Annotated[
    DeviceID,
    PlainValidator(lambda x: x if isinstance(x, DeviceID) else DeviceID(x)),
    PlainSerializer(lambda x: x.str, return_type=str),
]
InvitationTokenField = Annotated[
    InvitationToken,
    PlainValidator(lambda x: x if isinstance(x, InvitationToken) else InvitationToken.from_hex(x)),
    PlainSerializer(lambda x: x.hex, return_type=str),
]
InvitationStatusField = Annotated[
    InvitationStatus,
    PlainValidator(
        lambda x: x if isinstance(x, InvitationStatus) else InvitationStatus.from_str(x)
    ),
    PlainSerializer(lambda x: x.str, return_type=str),
]
RealmRoleField = Annotated[
    RealmRole,
    PlainValidator(lambda x: x if isinstance(x, RealmRole) else RealmRole.from_str(x)),
    PlainSerializer(lambda x: x.str, return_type=str),
]
VlobIDField = Annotated[
    VlobID,
    PlainValidator(lambda x: x if isinstance(x, VlobID) else VlobID.from_hex(x)),
    PlainSerializer(lambda x: x.hex, return_type=str),
]
DateTimeField = Annotated[
    DateTime,
    PlainValidator(lambda x: x if isinstance(x, DateTime) else DateTime.from_rfc3339(x)),
    PlainSerializer(lambda x: x.to_rfc3339, return_type=str),
]
UserProfileField = Annotated[
    UserProfile,
    PlainValidator(lambda x: x if isinstance(x, UserProfile) else UserProfile.from_str(x)),
    PlainSerializer(lambda x: x.str, return_type=str),
]
ActiveUsersLimitField = Annotated[
    ActiveUsersLimit,
    PlainValidator(
        lambda x: x if isinstance(x, ActiveUsersLimit) else ActiveUsersLimit.from_maybe_int(x)
    ),
    PlainSerializer(lambda x: x.to_maybe_int(), return_type=int | None),
]


class ClientBroadcastableEvent(ABC):
    event_id: UUID

    def is_event_for_client(self, client: RegisteredClient) -> bool:
        ...

    def dump_as_apiv4_sse_payload(self) -> bytes:
        ...

    @staticmethod
    def _dump_as_apiv4_sse_payload(
        unit: authenticated_cmds.latest.events_listen.APIEvent, event_id: UUID | None
    ) -> bytes:
        data = authenticated_cmds.latest.events_listen.RepOk(unit=unit).dump()
        if event_id is None:
            return b"data:%b\n\n" % data
        else:
            return b"data:%b\nid:%b\n\n" % (b64encode(data), event_id.hex.encode("ascii"))


class EventPinged(BaseModel, ClientBroadcastableEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["PINGED"] = "PINGED"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    ping: str

    @override
    def is_event_for_client(self, client: RegisteredClient) -> bool:
        return self.organization_id == client.organization_id

    @override
    def dump_as_apiv4_sse_payload(self) -> bytes:
        return self._dump_as_apiv4_sse_payload(
            authenticated_cmds.latest.events_listen.APIEventPinged(self.ping), self.event_id
        )


class EventInvitation(BaseModel, ClientBroadcastableEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["INVITATION"] = "INVITATION"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    token: InvitationTokenField
    greeter: UserIDField
    status: InvitationStatusField

    @override
    def is_event_for_client(self, client: RegisteredClient) -> bool:
        return self.organization_id == client.organization_id and self.greeter == client.user_id

    @override
    def dump_as_apiv4_sse_payload(self) -> bytes:
        return self._dump_as_apiv4_sse_payload(
            authenticated_cmds.latest.events_listen.APIEventInvitation(
                token=self.token,
                invitation_status=self.status,
            ),
            self.event_id,
        )


class EventPkiEnrollment(BaseModel, ClientBroadcastableEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["PKI_ENROLLMENT"] = "PKI_ENROLLMENT"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    enrollment_id: EnrollmentID

    @override
    def is_event_for_client(self, client: RegisteredClient) -> bool:
        return (
            self.organization_id == client.organization_id and client.profile == UserProfile.ADMIN
        )

    @override
    def dump_as_apiv4_sse_payload(self) -> bytes:
        return self._dump_as_apiv4_sse_payload(
            authenticated_cmds.latest.events_listen.APIEventPkiEnrollment(), self.event_id
        )


class EventVlob(BaseModel, ClientBroadcastableEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["VLOB"] = "VLOB"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    author: DeviceIDField
    realm_id: VlobIDField
    timestamp: DateTime
    vlob_id: VlobIDField
    version: int
    blob: bytes | None
    last_common_certificate_timestamp: DateTime
    last_realm_certificate_timestamp: DateTime

    @override
    def is_event_for_client(self, client: RegisteredClient) -> bool:
        return self.organization_id == client.organization_id and self.realm_id in client.realms

    @override
    def dump_as_apiv4_sse_payload(self) -> bytes:
        return self._dump_as_apiv4_sse_payload(
            authenticated_cmds.latest.events_listen.APIEventVlob(
                realm_id=self.realm_id,
                vlob_id=self.vlob_id,
                author=self.author,
                timestamp=self.timestamp,
                version=self.version,
                blob=self.blob,
                last_common_certificate_timestamp=self.last_common_certificate_timestamp,
                last_realm_certificate_timestamp=self.last_realm_certificate_timestamp,
            ),
            self.event_id,
        )


class EventCommonCertificate(BaseModel, ClientBroadcastableEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["COMMON_CERTIFICATE"] = "COMMON_CERTIFICATE"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    timestamp: DateTime

    @override
    def is_event_for_client(self, client: RegisteredClient) -> bool:
        return self.organization_id == client.organization_id

    @override
    def dump_as_apiv4_sse_payload(self) -> bytes:
        return self._dump_as_apiv4_sse_payload(
            authenticated_cmds.latest.events_listen.APIEventCommonCertificate(
                timestamp=self.timestamp,
            ),
            self.event_id,
        )


class EventSequesterCertificate(BaseModel, ClientBroadcastableEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["SEQUESTER_CERTIFICATE"] = "SEQUESTER_CERTIFICATE"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    timestamp: DateTime

    @override
    def is_event_for_client(self, client: RegisteredClient) -> bool:
        return self.organization_id == client.organization_id

    @override
    def dump_as_apiv4_sse_payload(self) -> bytes:
        return self._dump_as_apiv4_sse_payload(
            authenticated_cmds.latest.events_listen.APIEventSequesterCertificate(
                timestamp=self.timestamp,
            ),
            self.event_id,
        )


class EventShamirRecoveryCertificate(BaseModel, ClientBroadcastableEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["SHAMIR_RECOVERY_CERTIFICATE"] = "SHAMIR_RECOVERY_CERTIFICATE"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    timestamp: DateTime
    participants: tuple[UserID]

    @override
    def is_event_for_client(self, client: RegisteredClient) -> bool:
        return (
            self.organization_id == client.organization_id and client.user_id in self.participants
        )

    @override
    def dump_as_apiv4_sse_payload(self) -> bytes:
        return self._dump_as_apiv4_sse_payload(
            authenticated_cmds.latest.events_listen.APIEventShamirRecoveryCertificate(
                timestamp=self.timestamp,
            ),
            self.event_id,
        )


class EventRealmCertificate(BaseModel, ClientBroadcastableEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["REALM_CERTIFICATE"] = "REALM_CERTIFICATE"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    timestamp: DateTime
    realm_id: VlobID
    user_id: UserID
    role_removed: bool

    @override
    def is_event_for_client(self, client: RegisteredClient) -> bool:
        return self.organization_id == client.organization_id and self.realm_id in client.realms

    @override
    def dump_as_apiv4_sse_payload(self) -> bytes:
        return self._dump_as_apiv4_sse_payload(
            authenticated_cmds.latest.events_listen.APIEventRealmCertificate(
                timestamp=self.timestamp,
                realm_id=self.realm_id,
            ),
            self.event_id,
        )


class EventOrganizationConfig(BaseModel, ClientBroadcastableEvent):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["ORGANIZATION_CONFIG"] = "ORGANIZATION_CONFIG"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    user_profile_outsider_allowed: bool
    active_users_limit: ActiveUsersLimitField

    @override
    def is_event_for_client(self, client: RegisteredClient) -> bool:
        return self.organization_id == client.organization_id

    @override
    def dump_as_apiv4_sse_payload(self) -> bytes:
        return self._dump_as_apiv4_sse_payload(
            authenticated_cmds.latest.events_listen.APIEventServerConfig(
                user_profile_outsider_allowed=self.user_profile_outsider_allowed,
                active_users_limit=self.active_users_limit,
            ),
            self.event_id,
        )


class EventEnrollmentConduit(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["ENROLLMENT_CONDUIT"] = "ENROLLMENT_CONDUIT"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    token: InvitationTokenField
    greeter: UserIDField


class EventOrganizationExpired(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["ORGANIZATION_EXPIRED"] = "ORGANIZATION_EXPIRED"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField


class EventUserRevoked(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["USER_REVOKED"] = "USER_REVOKED"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    user_id: UserID


class EventUserUpdated(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, strict=True)
    type: Literal["USER_UPDATED"] = "USER_UPDATED"
    event_id: UUID = Field(default_factory=uuid4)
    organization_id: OrganizationIDField
    user_id: UserID
    new_profile: UserProfile


type Event = (
    EventPinged
    | EventInvitation
    | EventPkiEnrollment
    | EventVlob
    | EventCommonCertificate
    | EventSequesterCertificate
    | EventShamirRecoveryCertificate
    | EventRealmCertificate
    | EventOrganizationConfig
    | EventEnrollmentConduit
    | EventOrganizationExpired
    | EventUserRevoked
    | EventUserUpdated
)


class AnyEvent(BaseModel):
    event: Event = Field(..., discriminator="type")