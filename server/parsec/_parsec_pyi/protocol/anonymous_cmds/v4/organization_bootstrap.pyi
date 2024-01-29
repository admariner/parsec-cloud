# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

# /!\ Autogenerated by misc/gen_protocol_typings.py, any modification will be lost !

from __future__ import annotations

from parsec._parsec import BootstrapToken, DateTime, VerifyKey

class Req:
    def __init__(
        self,
        bootstrap_token: BootstrapToken | None,
        root_verify_key: VerifyKey,
        user_certificate: bytes,
        device_certificate: bytes,
        redacted_user_certificate: bytes,
        redacted_device_certificate: bytes,
        sequester_authority_certificate: bytes | None,
    ) -> None: ...
    def dump(self) -> bytes: ...
    @property
    def bootstrap_token(self) -> BootstrapToken | None: ...
    @property
    def root_verify_key(self) -> VerifyKey: ...
    @property
    def user_certificate(self) -> bytes: ...
    @property
    def device_certificate(self) -> bytes: ...
    @property
    def redacted_user_certificate(self) -> bytes: ...
    @property
    def redacted_device_certificate(self) -> bytes: ...
    @property
    def sequester_authority_certificate(self) -> bytes | None: ...

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
    ) -> None: ...

class RepInvalidCertificate(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepOrganizationAlreadyBootstrapped(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepInvalidBootstrapToken(Rep):
    def __init__(
        self,
    ) -> None: ...

class RepTimestampOutOfBallpark(Rep):
    def __init__(
        self,
        ballpark_client_early_offset: float,
        ballpark_client_late_offset: float,
        server_timestamp: DateTime,
        client_timestamp: DateTime,
    ) -> None: ...
    @property
    def ballpark_client_early_offset(self) -> float: ...
    @property
    def ballpark_client_late_offset(self) -> float: ...
    @property
    def server_timestamp(self) -> DateTime: ...
    @property
    def client_timestamp(self) -> DateTime: ...
