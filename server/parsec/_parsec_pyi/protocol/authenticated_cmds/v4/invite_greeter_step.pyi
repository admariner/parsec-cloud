# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

# /!\ Autogenerated by misc/gen_protocol_typings.py, any modification will be lost !

from __future__ import annotations

from parsec._parsec import (
    CancelledGreetingAttemptReason,
    DateTime,
    GreeterOrClaimer,
    GreetingAttemptID,
    HashDigest,
    PublicKey,
)

class GreeterStep:
    pass

class GreeterStepWaitPeer(GreeterStep):
    def __init__(self, public_key: PublicKey) -> None: ...
    @property
    def public_key(self) -> PublicKey: ...

class GreeterStepGetHashedNonce(GreeterStep):
    def __init__(
        self,
    ) -> None: ...

class GreeterStepSendNonce(GreeterStep):
    def __init__(self, greeter_nonce: bytes) -> None: ...
    @property
    def greeter_nonce(self) -> bytes: ...

class GreeterStepGetNonce(GreeterStep):
    def __init__(
        self,
    ) -> None: ...

class GreeterStepWaitPeerTrust(GreeterStep):
    def __init__(
        self,
    ) -> None: ...

class GreeterStepSignifyTrust(GreeterStep):
    def __init__(
        self,
    ) -> None: ...

class GreeterStepGetPayload(GreeterStep):
    def __init__(
        self,
    ) -> None: ...

class GreeterStepSendPayload(GreeterStep):
    def __init__(self, greeter_payload: bytes) -> None: ...
    @property
    def greeter_payload(self) -> bytes: ...

class GreeterStepWaitPeerAcknowledgment(GreeterStep):
    def __init__(
        self,
    ) -> None: ...

class ClaimerStep:
    pass

class ClaimerStepWaitPeer(ClaimerStep):
    def __init__(self, public_key: PublicKey) -> None: ...
    @property
    def public_key(self) -> PublicKey: ...

class ClaimerStepSendHashedNonce(ClaimerStep):
    def __init__(self, hashed_nonce: HashDigest) -> None: ...
    @property
    def hashed_nonce(self) -> HashDigest: ...

class ClaimerStepGetNonce(ClaimerStep):
    def __init__(
        self,
    ) -> None: ...

class ClaimerStepSendNonce(ClaimerStep):
    def __init__(self, claimer_nonce: bytes) -> None: ...
    @property
    def claimer_nonce(self) -> bytes: ...

class ClaimerStepSignifyTrust(ClaimerStep):
    def __init__(
        self,
    ) -> None: ...

class ClaimerStepWaitPeerTrust(ClaimerStep):
    def __init__(
        self,
    ) -> None: ...

class ClaimerStepSendPayload(ClaimerStep):
    def __init__(self, claimer_payload: bytes) -> None: ...
    @property
    def claimer_payload(self) -> bytes: ...

class ClaimerStepGetPayload(ClaimerStep):
    def __init__(
        self,
    ) -> None: ...

class ClaimerStepAcknowledge(ClaimerStep):
    def __init__(
        self,
    ) -> None: ...

class Req:
    def __init__(self, greeting_attempt: GreetingAttemptID, greeter_step: GreeterStep) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def greeter_step(self) -> GreeterStep: ...
    @property
    def greeting_attempt(self) -> GreetingAttemptID: ...

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
    def __init__(self, claimer_step: ClaimerStep) -> None: ...
    @property
    def claimer_step(self) -> ClaimerStep: ...

class RepNotReady(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepInvitationCompleted(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepInvitationCancelled(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepAuthorNotAllowed(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepGreetingAttemptNotFound(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepGreetingAttemptNotJoined(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepGreetingAttemptCancelled(Rep):
    def __init__(
        self, origin: GreeterOrClaimer, timestamp: DateTime, reason: CancelledGreetingAttemptReason
    ) -> None: ...
    @property
    def origin(self) -> GreeterOrClaimer: ...
    @property
    def reason(self) -> CancelledGreetingAttemptReason: ...
    @property
    def timestamp(self) -> DateTime: ...

class RepStepTooAdvanced(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepStepMismatch(Rep):
    def __init__(
        self,
    ) -> None: ...
