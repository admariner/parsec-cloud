# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS
from __future__ import annotations

from dataclasses import dataclass, field
from typing import NoReturn
from uuid import uuid4

from parsec._parsec import (
    ApiVersion,
    DeviceID,
    InvitationToken,
    InvitationType,
    OrganizationID,
    UserID,
    VerifyKey,
)
from parsec.logging import ParsecBoundLogger, get_logger

logger = get_logger()


@dataclass(slots=True)
class AnonymousClientContext:
    client_api_version: ApiVersion
    settled_api_version: ApiVersion
    organization_id: OrganizationID
    organization_internal_id: int
    logger: ParsecBoundLogger = field(init=False)

    def __post_init__(self):
        self.logger = logger.bind(
            request=uuid4().hex,
            api=f"{self.settled_api_version.version}.{self.settled_api_version.revision}",
            auth="anonymous",
            organization=self.organization_id.str,
        )

    def organization_not_found_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.OrganizationNotFound,
            api_version=self.settled_api_version,
        )

    def organization_expired_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.OrganizationExpired,
            api_version=self.settled_api_version,
        )


@dataclass(slots=True)
class InvitedClientContext:
    client_api_version: ApiVersion
    settled_api_version: ApiVersion
    organization_id: OrganizationID
    token: InvitationToken
    type: InvitationType
    organization_internal_id: int
    invitation_internal_id: int
    logger: ParsecBoundLogger = field(init=False)

    def __post_init__(self):
        self.logger = logger.bind(
            request=uuid4().hex,
            api=f"{self.settled_api_version.version}.{self.settled_api_version.revision}",
            auth="invited",
            organization=self.organization_id.str,
            token=self.token.hex,
        )

    def organization_not_found_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.OrganizationNotFound,
            api_version=self.settled_api_version,
        )

    def organization_expired_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.OrganizationExpired,
            api_version=self.settled_api_version,
        )

    def invitation_invalid_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.BadAuthenticationInfo,
            api_version=self.settled_api_version,
        )


@dataclass(slots=True)
class AuthenticatedClientContext:
    client_api_version: ApiVersion
    settled_api_version: ApiVersion
    organization_id: OrganizationID
    device_id: DeviceID
    device_verify_key: VerifyKey
    organization_internal_id: int
    device_internal_id: int
    logger: ParsecBoundLogger = field(init=False)
    _user_id: UserID | None = None

    def __post_init__(self):
        self.logger = logger.bind(
            request=uuid4().hex,
            api=f"{self.settled_api_version.version}.{self.settled_api_version.revision}",
            auth="authenticated",
            organization=self.organization_id.str,
            device=self.device_id.str,
        )

    @property
    def user_id(self) -> UserID:
        # UserId is costly to retrieve given it must be generated from DeviceID
        # then converted from Rust to Python !
        if self._user_id is None:
            self._user_id = self.device_id.user_id
        return self._user_id

    def organization_not_found_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.OrganizationNotFound,
            api_version=self.settled_api_version,
        )

    def organization_expired_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.OrganizationExpired,
            api_version=self.settled_api_version,
        )

    def author_not_found_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.BadAuthenticationInfo,
            api_version=self.settled_api_version,
        )

    def author_revoked_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.UserRevoked,
            api_version=self.settled_api_version,
        )
