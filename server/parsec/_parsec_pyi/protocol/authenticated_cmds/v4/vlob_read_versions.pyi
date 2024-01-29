# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

# /!\ Autogenerated by misc/gen_protocol_typings.py, any modification will be lost !

from __future__ import annotations

from parsec._parsec import DateTime, DeviceID, VlobID

class Req:
    def __init__(self, realm_id: VlobID, items: list[tuple[VlobID, int]]) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def realm_id(self) -> VlobID: ...
    @property
    def items(self) -> list[tuple[VlobID, int]]: ...

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
    def __init__(
        self,
        items: list[tuple[VlobID, int, DeviceID, int, DateTime, bytes]],
        needed_common_certificate_timestamp: DateTime,
        needed_realm_certificate_timestamp: DateTime,
    ) -> None: ...
    @property
    def items(self) -> list[tuple[VlobID, int, DeviceID, int, DateTime, bytes]]: ...
    @property
    def needed_common_certificate_timestamp(self) -> DateTime: ...
    @property
    def needed_realm_certificate_timestamp(self) -> DateTime: ...

class RepRealmNotFound(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepAuthorNotAllowed(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepTooManyElements(Rep):
    def __init__(
        self,
    ) -> None: ...
