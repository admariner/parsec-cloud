# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast, override

import anyio

from parsec._parsec import (
    ActiveUsersLimit,
    OrganizationID,
    UserID,
    UserProfile,
    VlobID,
)
from parsec.components.events import BaseEventsComponent, EventBus, SseAPiEventsListenBadOutcome
from parsec.components.postgresql import AsyncpgConnection, AsyncpgPool
from parsec.components.postgresql.handler import parse_signal, send_signal
from parsec.components.postgresql.organization import PGOrganizationComponent
from parsec.components.postgresql.realm import PGRealmComponent
from parsec.components.postgresql.user import PGUserComponent
from parsec.components.postgresql.utils import Q, transaction
from parsec.config import AccountVaultStrategy, AllowedClientAgent, BackendConfig
from parsec.events import Event, EventOrganizationConfig
from parsec.logging import get_logger

logger = get_logger()


class PGEventBus(EventBus):
    """The `EventBus.send` method is not implemented for the PostgreSQL event bus.

    Events are typically sent after a change in the database, meaning that there is
    always an open transaction to commit. For better concurrency handling, it makes
    more sense to send the event as part of the transaction, i.e using:

        await send_signal(conn, event)

    instead of using another connection such as the notification connection used
    in `test_send` for testing purposes.
    """

    def __init__(self, conn: AsyncpgConnection):
        super().__init__()
        self._conn = conn

    @override
    async def test_send(self, event: Event) -> None:
        await send_signal(self._conn, event)


@asynccontextmanager
async def event_bus_factory(pool: AsyncpgPool) -> AsyncIterator[PGEventBus]:
    _connection_lost = False

    def _on_notification_conn_termination(conn: object) -> None:
        nonlocal _connection_lost
        _connection_lost = True
        cancel_scope.cancel()

    def _on_notification(conn: object, pid: int, channel: str, payload: object) -> None:
        assert isinstance(payload, str)
        try:
            event = parse_signal(payload)
        except ValueError as exc:
            logger.warning(
                "Invalid notif received", pid=pid, channel=channel, payload=payload, exc_info=exc
            )
            return
        logger.info_with_debug_extra(
            "Dispatching event",
            type=event.type,
            event_id=event.event_id.hex,
            organization_id=event.organization_id.str,
            debug_extra=event.model_dump(),
        )
        event_bus._dispatch_incoming_event(event)

    try:
        async with pool.acquire() as notification_conn:
            conn = cast(AsyncpgConnection, notification_conn)
            event_bus = PGEventBus(conn)

            with anyio.CancelScope() as cancel_scope:
                notification_conn.add_termination_listener(_on_notification_conn_termination)

                await notification_conn.add_listener("app_notification", _on_notification)
                try:
                    yield event_bus
                finally:
                    await notification_conn.remove_listener("app_notification", _on_notification)

    finally:
        if _connection_lost:
            raise ConnectionError("PostgreSQL notification query has been lost")


_q_get_orga_and_user_infos = Q("""
WITH my_organization AS (
    SELECT
        _id,
        is_expired,
        user_profile_outsider_allowed,
        active_users_limit,
        allowed_client_agent,
        account_vault_strategy
    FROM organization
    WHERE
        organization_id = $organization_id
        -- Only consider bootstrapped organizations
        AND root_verify_key IS NOT NULL
    LIMIT 1
),

my_user AS (
    SELECT
        _id,
        user_id,
        current_profile,
        (revoked_on IS NOT NULL) AS revoked
    FROM user_
    WHERE
        user_id = $user_id
        AND organization = (SELECT my_organization._id FROM my_organization)
    LIMIT 1
),

-- Retrieve the last role for each realm the user is or used to be part of...
my_realms_last_roles AS (
    SELECT DISTINCT ON (realm)
        realm,
        role
    FROM realm_user_role
    WHERE user_ = (SELECT my_user._id FROM my_user)
    ORDER BY realm ASC, certified_on DESC
),

-- ...and only keep the realm the user is still part of
my_realms AS (
    SELECT
        (
            SELECT realm.realm_id FROM realm
            WHERE realm._id = my_realms_last_roles.realm
        )
    FROM my_realms_last_roles
    WHERE role IS NOT NULL
)

SELECT
    (SELECT _id FROM my_organization) AS organization_internal_id,
    (SELECT is_expired FROM my_organization) AS organization_is_expired,
    (SELECT user_profile_outsider_allowed FROM my_organization) AS organization_user_profile_outsider_allowed,
    (SELECT active_users_limit FROM my_organization) AS organization_active_users_limit,
    (SELECT allowed_client_agent FROM my_organization) AS organization_allowed_client_agent,
    (SELECT account_vault_strategy FROM my_organization) AS organization_account_vault_strategy,
    (SELECT _id FROM my_user) AS user_internal_id,
    (SELECT revoked FROM my_user) AS user_is_revoked,
    (SELECT user_id FROM my_user) AS user_id,
    (SELECT current_profile FROM my_user) AS user_current_profile,
    (SELECT ARRAY_AGG(realm_id) FROM my_realms) AS user_realms
""")


class PGEventsComponent(BaseEventsComponent):
    def __init__(self, pool: AsyncpgPool, config: BackendConfig, event_bus: EventBus):
        super().__init__(config, event_bus)
        self.pool = pool
        self.organization: PGOrganizationComponent
        self.user: PGUserComponent
        self.realm: PGRealmComponent

    def register_components(
        self,
        organization: PGOrganizationComponent,
        user: PGUserComponent,
        realm: PGRealmComponent,
        **kwargs,
    ) -> None:
        self.organization = organization
        self.user = user
        self.realm = realm

    @override
    @transaction
    async def _get_registration_info_for_user(
        self, conn: AsyncpgConnection, organization_id: OrganizationID, user_id: UserID
    ) -> tuple[EventOrganizationConfig, UserProfile, set[VlobID]] | SseAPiEventsListenBadOutcome:
        row = await conn.fetchrow(
            *_q_get_orga_and_user_infos(organization_id=organization_id.str, user_id=user_id)
        )
        assert row is not None

        # 1) Check organization

        match row["organization_internal_id"]:
            case int():
                pass
            case None:
                return SseAPiEventsListenBadOutcome.ORGANIZATION_NOT_FOUND
            case _:
                assert False, row

        match row["organization_is_expired"]:
            case False:
                pass
            case True:
                return SseAPiEventsListenBadOutcome.ORGANIZATION_EXPIRED
            case _:
                assert False, row

        match row["organization_user_profile_outsider_allowed"]:
            case bool() as organization_user_profile_outsider_allowed:
                pass
            case _:
                assert False, row

        match row["organization_active_users_limit"]:
            case None as organization_active_users_limit:
                organization_active_users_limit = ActiveUsersLimit.NO_LIMIT
            case int() as organization_active_users_limit:
                organization_active_users_limit = ActiveUsersLimit.limited_to(
                    organization_active_users_limit
                )
            case _:
                assert False, row

        match row["organization_allowed_client_agent"]:
            case str() as allowed_client_agent_raw:
                allowed_client_agent = AllowedClientAgent(allowed_client_agent_raw)
            case _:
                assert False, row

        match row["organization_account_vault_strategy"]:
            case str() as account_vault_strategy_raw:
                account_vault_strategy = AccountVaultStrategy(account_vault_strategy_raw)
            case _:
                assert False, row

        # 2) Check user

        match row["user_internal_id"]:
            case int():
                pass
            case None:
                return SseAPiEventsListenBadOutcome.AUTHOR_NOT_FOUND
            case _:
                assert False, row

        match row["user_id"]:
            case str() as raw_user_id:
                user_id = UserID.from_hex(raw_user_id)
            case _:
                assert False, row

        match row["user_is_revoked"]:
            case False:
                pass
            case True:
                return SseAPiEventsListenBadOutcome.AUTHOR_REVOKED
            case _:
                assert False, row

        match row["user_current_profile"]:
            case str() as raw_user_current_profile:
                user_current_profile = UserProfile.from_str(raw_user_current_profile)
            case _:
                assert False, row

        # 3) Check realms

        match row["user_realms"]:
            case list() as raw_user_realms:
                user_realms = set(VlobID.from_hex(x) for x in raw_user_realms)
            case None:
                user_realms = set()
            case _:
                assert False, row

        org_config = EventOrganizationConfig(
            organization_id=organization_id,
            user_profile_outsider_allowed=organization_user_profile_outsider_allowed,
            active_users_limit=organization_active_users_limit,
            allowed_client_agent=allowed_client_agent,
            account_vault_strategy=account_vault_strategy,
        )

        return org_config, user_current_profile, user_realms
