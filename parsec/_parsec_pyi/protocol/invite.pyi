# Parsec Cloud (https://parsec.cloud) Copyright (c) AGPL-3.0 2016-present Scille SAS

from __future__ import annotations

# Invite
from parsec._parsec import (
    DateTime,
    HashDigest,
    HumanHandle,
    InvitationDeletedReason,
    InvitationEmailSentStatus,
    InvitationStatus,
    InvitationToken,
    InvitationType,
    PublicKey,
    UserID,
)

class Invite1GreeterWaitPeerReq:
    def __init__(self, token: InvitationToken, greeter_public_key: PublicKey) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def token(self) -> InvitationToken: ...
    @property
    def greeter_public_key(self) -> PublicKey: ...

class Invite1GreeterWaitPeerRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite1GreeterWaitPeerRep: ...

class Invite1GreeterWaitPeerRepOk(Invite1GreeterWaitPeerRep):
    def __init__(self, claimer_public_key: PublicKey) -> None: ...
    @property
    def claimer_public_key(self) -> PublicKey: ...

class Invite1GreeterWaitPeerRepNotFound(Invite1GreeterWaitPeerRep): ...
class Invite1GreeterWaitPeerRepAlreadyDeleted(Invite1GreeterWaitPeerRep): ...
class Invite1GreeterWaitPeerRepInvalidState(Invite1GreeterWaitPeerRep): ...

class Invite1GreeterWaitPeerRepUnknownStatus(Invite1GreeterWaitPeerRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite2aGreeterGetHashedNonceReq:
    def __init__(self, token: InvitationToken) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def token(self) -> InvitationToken: ...

class Invite2aGreeterGetHashedNonceRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite2aGreeterGetHashedNonceRep: ...

class Invite2aGreeterGetHashedNonceRepOk(Invite2aGreeterGetHashedNonceRep):
    def __init__(self, claimer_hashed_nonce: HashDigest) -> None: ...
    @property
    def claimer_hashed_nonce(self) -> HashDigest: ...

class Invite2aGreeterGetHashedNonceRepNotFound(Invite2aGreeterGetHashedNonceRep): ...
class Invite2aGreeterGetHashedNonceRepAlreadyDeleted(Invite2aGreeterGetHashedNonceRep): ...
class Invite2aGreeterGetHashedNonceRepInvalidState(Invite2aGreeterGetHashedNonceRep): ...

class Invite2aGreeterGetHashedNonceRepUnknownStatus(Invite2aGreeterGetHashedNonceRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite2bGreeterSendNonceReq:
    def __init__(self, token: InvitationToken, greeter_nonce: bytes) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def token(self) -> InvitationToken: ...
    @property
    def greeter_nonce(self) -> bytes: ...

class Invite2bGreeterSendNonceRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite2bGreeterSendNonceRep: ...

class Invite2bGreeterSendNonceRepOk(Invite2bGreeterSendNonceRep):
    def __init__(self, claimer_nonce: bytes) -> None: ...
    @property
    def claimer_nonce(self) -> bytes: ...

class Invite2bGreeterSendNonceRepNotFound(Invite2bGreeterSendNonceRep): ...
class Invite2bGreeterSendNonceRepAlreadyDeleted(Invite2bGreeterSendNonceRep): ...
class Invite2bGreeterSendNonceRepInvalidState(Invite2bGreeterSendNonceRep): ...

class Invite2bGreeterSendNonceRepUnknownStatus(Invite2bGreeterSendNonceRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite3aGreeterWaitPeerTrustReq:
    def __init__(self, token: InvitationToken) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def token(self) -> InvitationToken: ...

class Invite3aGreeterWaitPeerTrustRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite3aGreeterWaitPeerTrustRep: ...

class Invite3aGreeterWaitPeerTrustRepOk(Invite3aGreeterWaitPeerTrustRep): ...
class Invite3aGreeterWaitPeerTrustRepNotFound(Invite3aGreeterWaitPeerTrustRep): ...
class Invite3aGreeterWaitPeerTrustRepAlreadyDeleted(Invite3aGreeterWaitPeerTrustRep): ...
class Invite3aGreeterWaitPeerTrustRepInvalidState(Invite3aGreeterWaitPeerTrustRep): ...

class Invite3aGreeterWaitPeerTrustRepUnknownStatus(Invite3aGreeterWaitPeerTrustRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite3bGreeterSignifyTrustReq:
    def __init__(self, token: InvitationToken) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def token(self) -> InvitationToken: ...

class Invite3bGreeterSignifyTrustRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite3bGreeterSignifyTrustRep: ...

class Invite3bGreeterSignifyTrustRepOk(Invite3bGreeterSignifyTrustRep): ...
class Invite3bGreeterSignifyTrustRepNotFound(Invite3bGreeterSignifyTrustRep): ...
class Invite3bGreeterSignifyTrustRepAlreadyDeleted(Invite3bGreeterSignifyTrustRep): ...
class Invite3bGreeterSignifyTrustRepInvalidState(Invite3bGreeterSignifyTrustRep): ...

class Invite3bGreeterSignifyTrustRepUnknownStatus(Invite3bGreeterSignifyTrustRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite4GreeterCommunicateReq:
    def __init__(self, token: InvitationToken, payload: bytes) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def token(self) -> InvitationToken: ...
    @property
    def payload(self) -> bytes: ...

class Invite4GreeterCommunicateRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite4GreeterCommunicateRep: ...

class Invite4GreeterCommunicateRepOk(Invite4GreeterCommunicateRep):
    def __init__(self, payload: bytes) -> None: ...
    @property
    def payload(self) -> bytes: ...

class Invite4GreeterCommunicateRepNotFound(Invite4GreeterCommunicateRep): ...
class Invite4GreeterCommunicateRepAlreadyDeleted(Invite4GreeterCommunicateRep): ...
class Invite4GreeterCommunicateRepInvalidState(Invite4GreeterCommunicateRep): ...

class Invite4GreeterCommunicateRepUnknownStatus(Invite4GreeterCommunicateRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class InviteDeleteReq:
    def __init__(self, token: InvitationToken, reason: InvitationDeletedReason) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def token(self) -> InvitationToken: ...
    @property
    def reason(self) -> InvitationDeletedReason: ...

class InviteDeleteRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> InviteDeleteRep: ...

class InviteDeleteRepOk(InviteDeleteRep): ...
class InviteDeleteRepNotFound(InviteDeleteRep): ...
class InviteDeleteRepAlreadyDeleted(InviteDeleteRep): ...

class InviteDeleteRepUnknownStatus(InviteDeleteRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class InviteListReq:
    def dump(self) -> bytes: ...

class InviteListRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> InviteListRep: ...

class InviteListRepUnknownStatus(InviteListRep):
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class InviteListItem:
    @classmethod
    def User(
        cls,
        token: InvitationToken,
        created_on: DateTime,
        claimer_email: str,
        status: InvitationStatus,
    ) -> InviteListItem: ...
    @classmethod
    def Device(
        cls, token: InvitationToken, created_on: DateTime, status: InvitationStatus
    ) -> InviteListItem: ...
    @property
    def type(self) -> InvitationType: ...
    @property
    def token(self) -> InvitationToken: ...
    @property
    def created_on(self) -> DateTime: ...
    @property
    def status(self) -> InvitationStatus: ...
    @property
    def claimer_email(self) -> str: ...

class InviteListRepOk(InviteListRep):
    def __init__(self, invitations: list[InviteListItem]) -> None: ...
    @property
    def invitations(self) -> list[InviteListItem]: ...

class InviteNewReq:
    def __init__(
        self, type: InvitationType, claimer_email: str | None, send_email: bool
    ) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def type(self) -> InvitationType: ...
    @property
    def claimer_email(self) -> str: ...
    @property
    def send_email(self) -> bool: ...

class InviteNewRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> InviteNewRep: ...

class InviteNewRepOk(InviteNewRep):
    def __init__(
        self, token: InvitationToken, email_sent: InvitationEmailSentStatus | None
    ) -> None: ...
    @property
    def token(self) -> InvitationToken: ...
    @property
    def email_sent(self) -> InvitationEmailSentStatus: ...

class InviteNewRepNotAllowed(InviteNewRep): ...
class InviteNewRepAlreadyMember(InviteNewRep): ...
class InviteNewRepNotAvailable(InviteNewRep): ...

class InviteNewRepUnknownStatus(InviteNewRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite1ClaimerWaitPeerReq:
    def __init__(self, claimer_public_key: PublicKey) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def claimer_public_key(self) -> PublicKey: ...

class Invite1ClaimerWaitPeerRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite1ClaimerWaitPeerRep: ...

class Invite1ClaimerWaitPeerRepOk(Invite1ClaimerWaitPeerRep):
    def __init__(self, greeter_public_key: PublicKey) -> None: ...
    @property
    def greeter_public_key(self) -> PublicKey: ...

class Invite1ClaimerWaitPeerRepNotFound(Invite1ClaimerWaitPeerRep): ...
class Invite1ClaimerWaitPeerRepInvalidState(Invite1ClaimerWaitPeerRep): ...

class Invite1ClaimerWaitPeerRepUnknownStatus(Invite1ClaimerWaitPeerRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite2aClaimerSendHashedNonceReq:
    def __init__(self, claimer_hashed_nonce: HashDigest) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def claimer_hashed_nonce(self) -> HashDigest: ...

class Invite2aClaimerSendHashedNonceRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite2aClaimerSendHashedNonceRep: ...

class Invite2aClaimerSendHashedNonceRepOk(Invite2aClaimerSendHashedNonceRep):
    def __init__(self, greeter_nonce: bytes) -> None: ...
    @property
    def greeter_nonce(self) -> bytes: ...

class Invite2aClaimerSendHashedNonceRepNotFound(Invite2aClaimerSendHashedNonceRep): ...
class Invite2aClaimerSendHashedNonceRepAlreadyDeleted(Invite2aClaimerSendHashedNonceRep): ...
class Invite2aClaimerSendHashedNonceRepInvalidState(Invite2aClaimerSendHashedNonceRep): ...

class Invite2aClaimerSendHashedNonceRepUnknownStatus(Invite2aClaimerSendHashedNonceRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite2bClaimerSendNonceReq:
    def __init__(self, claimer_nonce: bytes) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def claimer_nonce(self) -> bytes: ...

class Invite2bClaimerSendNonceRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite2bClaimerSendNonceRep: ...

class Invite2bClaimerSendNonceRepOk(Invite2bClaimerSendNonceRep): ...
class Invite2bClaimerSendNonceRepNotFound(Invite2bClaimerSendNonceRep): ...
class Invite2bClaimerSendNonceRepInvalidState(Invite2bClaimerSendNonceRep): ...

class Invite2bClaimerSendNonceRepUnknownStatus(Invite2bClaimerSendNonceRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite3aClaimerSignifyTrustReq:
    def dump(self) -> bytes: ...

class Invite3aClaimerSignifyTrustRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite3aClaimerSignifyTrustRep: ...

class Invite3aClaimerSignifyTrustRepOk(Invite3aClaimerSignifyTrustRep): ...
class Invite3aClaimerSignifyTrustRepNotFound(Invite3aClaimerSignifyTrustRep): ...
class Invite3aClaimerSignifyTrustRepInvalidState(Invite3aClaimerSignifyTrustRep): ...

class Invite3aClaimerSignifyTrustRepUnknownStatus(Invite3aClaimerSignifyTrustRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite3bClaimerWaitPeerTrustReq:
    def dump(self) -> bytes: ...

class Invite3bClaimerWaitPeerTrustRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite3bClaimerWaitPeerTrustRep: ...

class Invite3bClaimerWaitPeerTrustRepOk(Invite3bClaimerWaitPeerTrustRep): ...
class Invite3bClaimerWaitPeerTrustRepNotFound(Invite3bClaimerWaitPeerTrustRep): ...
class Invite3bClaimerWaitPeerTrustRepInvalidState(Invite3bClaimerWaitPeerTrustRep): ...

class Invite3bClaimerWaitPeerTrustRepUnknownStatus(Invite3bClaimerWaitPeerTrustRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class Invite4ClaimerCommunicateReq:
    def __init__(self, payload: bytes) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def payload(self) -> bytes: ...

class Invite4ClaimerCommunicateRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> Invite4ClaimerCommunicateRep: ...

class Invite4ClaimerCommunicateRepOk(Invite4ClaimerCommunicateRep):
    def __init__(self, payload: bytes) -> None: ...
    @property
    def payload(self) -> bytes: ...

class Invite4ClaimerCommunicateRepNotFound(Invite4ClaimerCommunicateRep): ...
class Invite4ClaimerCommunicateRepInvalidState(Invite4ClaimerCommunicateRep): ...

class Invite4ClaimerCommunicateRepUnknownStatus(Invite4ClaimerCommunicateRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...

class InviteInfoReq:
    def dump(self) -> bytes: ...

class InviteInfoRep:
    def dump(self) -> bytes: ...
    @classmethod
    def load(cls, buf: bytes) -> InviteInfoRep: ...

class InviteInfoRepOk(InviteInfoRep):
    def __init__(
        self,
        type: InvitationType,
        claimer_email: str | None,
        greeter_user_id: UserID,
        greeter_human_handle: HumanHandle | None,
    ) -> None: ...
    @property
    def type(self) -> InvitationType: ...
    @property
    def claimer_email(self) -> str: ...
    @property
    def greeter_user_id(self) -> UserID: ...
    @property
    def greeter_human_handle(self) -> HumanHandle | None: ...

class InviteInfoRepUnknownStatus(InviteInfoRep):
    def __init__(self, status: str, reason: str | None) -> None: ...
    @property
    def status(self) -> str: ...
    @property
    def reason(self) -> str | None: ...
