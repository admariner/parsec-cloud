# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

# /!\ Autogenerated by misc/gen_protocol_typings.py, any modification will be lost !

from __future__ import annotations

from parsec._parsec import InvitationToken, PublicKey

class Req:
    def __init__(self, token: InvitationToken, greeter_public_key: PublicKey) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def token(self) -> InvitationToken: ...
    @property
    def greeter_public_key(self) -> PublicKey: ...

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
    def __init__(self, claimer_public_key: PublicKey) -> None: ...
    @property
    def claimer_public_key(self) -> PublicKey: ...

class RepInvitationNotFound(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepInvitationDeleted(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepEnrollmentWrongState(Rep):
    def __init__(
        self,
    ) -> None: ...
