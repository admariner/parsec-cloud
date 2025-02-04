# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

# /!\ Autogenerated by misc/gen_protocol_typings.py, any modification will be lost !

from __future__ import annotations

from parsec._parsec import (
    ActiveUsersLimit,
    DateTime,
    DeviceID,
    GreetingAttemptID,
    InvitationStatus,
    InvitationToken,
    VlobID,
)

class APIEvent:
    pass

class APIEventPinged(APIEvent):
    def __init__(self, ping: str) -> None: ...
    @property
    def ping(self) -> str: ...

class APIEventServerConfig(APIEvent):
    def __init__(
        self, user_profile_outsider_allowed: bool, active_users_limit: ActiveUsersLimit
    ) -> None: ...
    @property
    def active_users_limit(self) -> ActiveUsersLimit: ...
    @property
    def user_profile_outsider_allowed(self) -> bool: ...

class APIEventInvitation(APIEvent):
    def __init__(self, token: InvitationToken, invitation_status: InvitationStatus) -> None: ...
    @property
    def invitation_status(self) -> InvitationStatus: ...
    @property
    def token(self) -> InvitationToken: ...

class APIEventGreetingAttemptReady(APIEvent):
    def __init__(self, token: InvitationToken, greeting_attempt: GreetingAttemptID) -> None: ...
    @property
    def greeting_attempt(self) -> GreetingAttemptID: ...
    @property
    def token(self) -> InvitationToken: ...

class APIEventGreetingAttemptCancelled(APIEvent):
    def __init__(self, token: InvitationToken, greeting_attempt: GreetingAttemptID) -> None: ...
    @property
    def greeting_attempt(self) -> GreetingAttemptID: ...
    @property
    def token(self) -> InvitationToken: ...

class APIEventPkiEnrollment(APIEvent):
    def __init__(
        self,
    ) -> None: ...

class APIEventCommonCertificate(APIEvent):
    def __init__(self, timestamp: DateTime) -> None: ...
    @property
    def timestamp(self) -> DateTime: ...

class APIEventSequesterCertificate(APIEvent):
    def __init__(self, timestamp: DateTime) -> None: ...
    @property
    def timestamp(self) -> DateTime: ...

class APIEventShamirRecoveryCertificate(APIEvent):
    def __init__(self, timestamp: DateTime) -> None: ...
    @property
    def timestamp(self) -> DateTime: ...

class APIEventRealmCertificate(APIEvent):
    def __init__(self, timestamp: DateTime, realm_id: VlobID) -> None: ...
    @property
    def realm_id(self) -> VlobID: ...
    @property
    def timestamp(self) -> DateTime: ...

class APIEventVlob(APIEvent):
    def __init__(
        self,
        realm_id: VlobID,
        vlob_id: VlobID,
        author: DeviceID,
        timestamp: DateTime,
        version: int,
        blob: bytes | None,
        last_common_certificate_timestamp: DateTime,
        last_realm_certificate_timestamp: DateTime,
    ) -> None: ...
    @property
    def author(self) -> DeviceID: ...
    @property
    def blob(self) -> bytes | None: ...
    @property
    def last_common_certificate_timestamp(self) -> DateTime: ...
    @property
    def last_realm_certificate_timestamp(self) -> DateTime: ...
    @property
    def realm_id(self) -> VlobID: ...
    @property
    def timestamp(self) -> DateTime: ...
    @property
    def version(self) -> int: ...
    @property
    def vlob_id(self) -> VlobID: ...

class Req:
    def __init__(
        self,
    ) -> None: ...
    def dump(self) -> bytes: ...

class Rep:
    @staticmethod
    def load(raw: bytes) -> Rep: ...
    def dump(self) -> bytes: ...

class RepUnknownStatus(Rep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class RepOk(Rep):
    def __init__(self, unit: APIEvent) -> None: ...
    @property
    def unit(self) -> APIEvent: ...

class RepNotAvailable(Rep):
    def __init__(
        self,
    ) -> None: ...
