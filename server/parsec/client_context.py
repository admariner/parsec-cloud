# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, NoReturn
from uuid import uuid4

from parsec._parsec import (
    AccountAuthMethodID,
    ApiVersion,
    DeviceID,
    EmailAddress,
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
        # Generate a request ID just for the logs
        # It doesn't have to be as long as a UUID, 4 hex characters should be enough
        request_id = uuid4().hex[:4]
        self.logger = logger.bind(
            request=request_id,
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
        # Generate a request ID just for the logs
        # It doesn't have to be as long as a UUID, 4 hex characters should be enough
        request_id = uuid4().hex[:4]
        self.logger = logger.bind(
            request=request_id,
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

    def invitation_not_found_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.BadAuthenticationInfo,
            api_version=self.settled_api_version,
        )

    def invitation_already_used_or_deleted_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.InvitationAlreadyUsedOrDeleted,
            api_version=self.settled_api_version,
        )


@dataclass(slots=True)
class AuthenticatedClientContext:
    client_api_version: ApiVersion
    settled_api_version: ApiVersion
    organization_id: OrganizationID
    user_id: UserID
    device_id: DeviceID
    device_verify_key: VerifyKey
    organization_internal_id: int
    device_internal_id: int
    logger: ParsecBoundLogger = field(init=False)

    def __post_init__(self):
        # Generate a request ID just for the logs
        # It doesn't have to be as long as a UUID, 4 hex characters should be enough
        request_id = uuid4().hex[:4]
        self.logger = logger.bind(
            request=request_id,
            api=f"{self.settled_api_version.version}.{self.settled_api_version.revision}",
            auth="authenticated",
            organization=self.organization_id.str,
            device=self.device_id.hex,
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


@dataclass(slots=True)
class AnonymousAccountClientContext:
    client_api_version: ApiVersion
    settled_api_version: ApiVersion
    logger: ParsecBoundLogger = field(init=False)
    client_user_agent: str
    # In ASGI the client IP address is optional
    # see https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    client_ip_address: str | Literal[""]

    def __post_init__(self):
        # Generate a request ID just for the logs
        # It doesn't have to be as long as a UUID, 4 hex characters should be enough
        request_id = uuid4().hex[:4]
        self.logger = logger.bind(
            request=request_id,
            api=f"{self.settled_api_version.version}.{self.settled_api_version.revision}",
            auth="anonymous_account",
        )


@dataclass(slots=True)
class AuthenticatedAccountClientContext:
    client_api_version: ApiVersion
    settled_api_version: ApiVersion
    account_email: EmailAddress
    auth_method_id: AccountAuthMethodID
    client_user_agent: str
    # In ASGI the client IP address is optional
    # see https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
    client_ip_address: str | Literal[""]
    logger: ParsecBoundLogger = field(init=False)

    def __post_init__(self):
        # Generate a request ID just for the logs
        # It doesn't have to be as long as a UUID, 4 hex characters should be enough
        request_id = uuid4().hex[:4]
        self.logger = logger.bind(
            request=request_id,
            api=f"{self.settled_api_version.version}.{self.settled_api_version.revision}",
            auth="authenticated_account",
        )

    def account_not_found_abort(self) -> NoReturn:
        from parsec.asgi.rpc import CustomHttpStatus, _handshake_abort

        _handshake_abort(
            CustomHttpStatus.BadAuthenticationInfo,
            api_version=self.settled_api_version,
        )
