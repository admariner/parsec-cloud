# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS
from __future__ import annotations

from typing import Any, override

from parsec._parsec import (
    ActiveUsersLimit,
    BootstrapToken,
    DateTime,
    DeviceCertificate,
    DeviceID,
    OrganizationID,
    SequesterAuthorityCertificate,
    UserCertificate,
    UserProfile,
    VerifyKey,
)
from parsec.ballpark import TimestampOutOfBallpark
from parsec.components.events import EventBus
from parsec.components.memory.datamodel import (
    MemoryDatamodel,
    MemoryDevice,
    MemoryOrganization,
    MemoryUser,
)
from parsec.components.organization import (
    BaseOrganizationComponent,
    Organization,
    OrganizationBootstrapStoreBadOutcome,
    OrganizationBootstrapValidateBadOutcome,
    OrganizationCreateBadOutcome,
    OrganizationDump,
    OrganizationDumpTopics,
    OrganizationGetBadOutcome,
    OrganizationGetTosBadOutcome,
    OrganizationStats,
    OrganizationStatsAsUserBadOutcome,
    OrganizationStatsBadOutcome,
    OrganizationStatsProfileDetailItem,
    OrganizationUpdateBadOutcome,
    TermsOfService,
    TosLocale,
    TosUrl,
    organization_bootstrap_validate,
)
from parsec.config import AccountVaultStrategy, AllowedClientAgent
from parsec.events import EventOrganizationExpired, EventOrganizationTosUpdated
from parsec.types import Unset, UnsetType


class MemoryOrganizationComponent(BaseOrganizationComponent):
    def __init__(
        self,
        data: MemoryDatamodel,
        event_bus: EventBus,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._data = data
        self._event_bus = event_bus

    @override
    async def create(
        self,
        now: DateTime,
        id: OrganizationID,
        active_users_limit: UnsetType | ActiveUsersLimit = Unset,
        user_profile_outsider_allowed: UnsetType | bool = Unset,
        minimum_archiving_period: UnsetType | int = Unset,
        tos: UnsetType | dict[TosLocale, TosUrl] = Unset,
        allowed_client_agent: UnsetType | AllowedClientAgent = Unset,
        account_vault_strategy: UnsetType | AccountVaultStrategy = Unset,
        force_bootstrap_token: BootstrapToken | None = None,
    ) -> BootstrapToken | OrganizationCreateBadOutcome:
        if minimum_archiving_period is not Unset:
            assert minimum_archiving_period >= 0  # Sanity check

        bootstrap_token = force_bootstrap_token or BootstrapToken.new()
        org = self._data.organizations.get(id)
        # Allow overwriting of not-yet-bootstrapped organization
        if org and org.root_verify_key:
            return OrganizationCreateBadOutcome.ORGANIZATION_ALREADY_EXISTS
        if active_users_limit is Unset:
            active_users_limit = self._config.organization_initial_active_users_limit
        assert isinstance(active_users_limit, ActiveUsersLimit)
        if user_profile_outsider_allowed is Unset:
            user_profile_outsider_allowed = (
                self._config.organization_initial_user_profile_outsider_allowed
            )
        assert isinstance(user_profile_outsider_allowed, bool)
        if minimum_archiving_period is Unset:
            minimum_archiving_period = self._config.organization_initial_minimum_archiving_period
        assert isinstance(minimum_archiving_period, int)
        if tos is Unset:
            if self._config.organization_initial_tos is None:
                cooked_tos = None
            else:
                cooked_tos = TermsOfService(
                    updated_on=now, per_locale_urls=self._config.organization_initial_tos
                )
        else:
            cooked_tos = TermsOfService(updated_on=now, per_locale_urls=tos)
        if allowed_client_agent is Unset:
            allowed_client_agent = self._config.organization_initial_allowed_client_agent
        assert isinstance(allowed_client_agent, AllowedClientAgent)
        if account_vault_strategy is Unset:
            account_vault_strategy = self._config.organization_initial_account_vault_strategy
        assert isinstance(account_vault_strategy, AccountVaultStrategy)

        self._data.organizations[id] = MemoryOrganization(
            organization_id=id,
            bootstrap_token=bootstrap_token,
            user_profile_outsider_allowed=user_profile_outsider_allowed,
            active_users_limit=active_users_limit,
            minimum_archiving_period=minimum_archiving_period,
            tos=cooked_tos,
            allowed_client_agent=allowed_client_agent,
            account_vault_strategy=account_vault_strategy,
            created_on=now,
        )

        return bootstrap_token

    @override
    async def get(self, id: OrganizationID) -> Organization | OrganizationGetBadOutcome:
        try:
            org = self._data.organizations[id]
        except KeyError:
            return OrganizationGetBadOutcome.ORGANIZATION_NOT_FOUND

        if org.sequester_authority_certificate is not None:
            assert org.cooked_sequester_authority is not None
            sequester_authority_verify_key_der = org.cooked_sequester_authority.verify_key_der
            assert org.sequester_services is not None
            sequester_services_certificates = tuple(
                s.sequester_service_certificate for s in org.sequester_services.values()
            )
        else:
            sequester_authority_verify_key_der = None
            sequester_services_certificates = None

        return Organization(
            organization_id=org.organization_id,
            bootstrap_token=org.bootstrap_token,
            is_expired=org.is_expired,
            created_on=org.created_on,
            bootstrapped_on=org.bootstrapped_on,
            root_verify_key=org.root_verify_key,
            user_profile_outsider_allowed=org.user_profile_outsider_allowed,
            active_users_limit=org.active_users_limit,
            minimum_archiving_period=org.minimum_archiving_period,
            sequester_authority_certificate=org.sequester_authority_certificate,
            sequester_authority_verify_key_der=sequester_authority_verify_key_der,
            sequester_services_certificates=sequester_services_certificates,
            tos=org.tos,
            allowed_client_agent=org.allowed_client_agent,
            account_vault_strategy=org.account_vault_strategy,
        )

    @override
    async def bootstrap(
        self,
        id: OrganizationID,
        now: DateTime,
        bootstrap_token: BootstrapToken | None,
        root_verify_key: VerifyKey,
        user_certificate: bytes,
        device_certificate: bytes,
        redacted_user_certificate: bytes,
        redacted_device_certificate: bytes,
        sequester_authority_certificate: bytes | None,
    ) -> (
        tuple[UserCertificate, DeviceCertificate, SequesterAuthorityCertificate | None]
        | OrganizationBootstrapValidateBadOutcome
        | OrganizationBootstrapStoreBadOutcome
        | TimestampOutOfBallpark
    ):
        try:
            org = self._data.organizations[id]
        except KeyError:
            return OrganizationBootstrapStoreBadOutcome.ORGANIZATION_NOT_FOUND

        async with org.topics_lock(write=["common"]):
            if org.is_expired:
                return OrganizationBootstrapStoreBadOutcome.ORGANIZATION_EXPIRED

            if org.bootstrap_token != bootstrap_token:
                return OrganizationBootstrapStoreBadOutcome.INVALID_BOOTSTRAP_TOKEN

            if org.is_bootstrapped:
                return OrganizationBootstrapStoreBadOutcome.ORGANIZATION_ALREADY_BOOTSTRAPPED

            match organization_bootstrap_validate(
                now=now,
                root_verify_key=root_verify_key,
                user_certificate=user_certificate,
                device_certificate=device_certificate,
                redacted_user_certificate=redacted_user_certificate,
                redacted_device_certificate=redacted_device_certificate,
                sequester_authority_certificate=sequester_authority_certificate,
            ):
                case (u_certif, d_certif, s_certif):
                    pass
                case error:
                    return error

            # All checks are good, now we do the actual insertion

            org.per_topic_last_timestamp["common"] = u_certif.timestamp

            org.bootstrapped_on = now
            assert org.root_verify_key is None
            org.root_verify_key = root_verify_key

            # Organization is empty, so nothing can go wrong when inserting user & device

            assert not org.users
            org.users[u_certif.user_id] = MemoryUser(
                cooked=u_certif,
                user_certificate=user_certificate,
                redacted_user_certificate=redacted_user_certificate,
            )

            assert not org.devices
            org.devices[d_certif.device_id] = MemoryDevice(
                cooked=d_certif,
                device_certificate=device_certificate,
                redacted_device_certificate=redacted_device_certificate,
            )

            assert org.sequester_authority_certificate is None
            assert org.cooked_sequester_authority is None
            assert org.sequester_services is None
            if s_certif:
                org.per_topic_last_timestamp["sequester"] = s_certif.timestamp
                org.sequester_authority_certificate = sequester_authority_certificate
                org.cooked_sequester_authority = s_certif
                org.sequester_services = {}

            return u_certif, d_certif, s_certif

    @override
    async def stats(
        self,
        organization_id: OrganizationID,
        author: DeviceID,
        at: DateTime | None = None,
    ) -> OrganizationStats | OrganizationStatsAsUserBadOutcome:
        try:
            org = self._data.organizations[organization_id]
        except KeyError:
            return OrganizationStatsAsUserBadOutcome.ORGANIZATION_NOT_FOUND
        if org.is_expired:
            return OrganizationStatsAsUserBadOutcome.ORGANIZATION_EXPIRED

        try:
            device = org.devices[author]
        except KeyError:
            return OrganizationStatsAsUserBadOutcome.AUTHOR_NOT_FOUND

        try:
            user = org.users[device.cooked.user_id]
        except KeyError:
            return OrganizationStatsAsUserBadOutcome.AUTHOR_NOT_FOUND

        if user.is_revoked:
            return OrganizationStatsAsUserBadOutcome.AUTHOR_REVOKED

        if user.current_profile != UserProfile.ADMIN:
            return OrganizationStatsAsUserBadOutcome.AUTHOR_NOT_ALLOWED

        match self._stats(org, at):
            case OrganizationStats() as stats:
                return stats
            case OrganizationStatsBadOutcome.ORGANIZATION_NOT_FOUND:
                return OrganizationStatsAsUserBadOutcome.ORGANIZATION_NOT_FOUND

    def _stats(
        self,
        org: MemoryOrganization,
        at: DateTime | None,
    ) -> OrganizationStats | OrganizationStatsBadOutcome:
        at = at or DateTime.now()

        if org.created_on > at:
            return OrganizationStatsBadOutcome.ORGANIZATION_NOT_FOUND

        users = 0
        active_users = 0
        users_per_profile_detail = {p: {"active": 0, "revoked": 0} for p in UserProfile.VALUES}
        for user in org.users.values():
            if user.cooked.timestamp > at:
                continue
            users += 1
            if user.cooked_revoked and user.cooked_revoked.timestamp <= at:
                users_per_profile_detail[user.current_profile]["revoked"] += 1
            else:
                users_per_profile_detail[user.current_profile]["active"] += 1
                active_users += 1

        realms = 0
        metadata_size = 0
        data_size = 0
        for realm in org.realms.values():
            if realm.created_on <= at:
                realms += 1
        for realm in org.realms.values():
            for vlob in realm.vlobs.values():
                metadata_size += sum(len(atom.blob) for atom in vlob if atom.created_on <= at)
        for block in org.blocks.values():
            if block.created_on <= at:
                data_size += block.block_size

        users_per_profile_detail = tuple(
            OrganizationStatsProfileDetailItem(profile=profile, **data)
            for profile, data in users_per_profile_detail.items()
        )
        return OrganizationStats(
            data_size=data_size,
            metadata_size=metadata_size,
            realms=realms,
            users=users,
            active_users=active_users,
            users_per_profile_detail=users_per_profile_detail,
        )

    @override
    async def organization_stats(
        self,
        organization_id: OrganizationID,
    ) -> OrganizationStats | OrganizationStatsBadOutcome:
        try:
            org = self._data.organizations[organization_id]
        except KeyError:
            return OrganizationStatsBadOutcome.ORGANIZATION_NOT_FOUND
        match self._stats(org, None):
            case OrganizationStats() as stats:
                return stats
            case OrganizationStatsBadOutcome.ORGANIZATION_NOT_FOUND:
                return OrganizationStatsBadOutcome.ORGANIZATION_NOT_FOUND

    @override
    async def server_stats(
        self, at: DateTime | None = None
    ) -> dict[OrganizationID, OrganizationStats]:
        at = at or DateTime.now()

        result = {}
        for org_id, org in sorted(self._data.organizations.items()):
            match self._stats(org, at):
                case OrganizationStats() as stats:
                    result[org_id] = stats
                case OrganizationStatsBadOutcome.ORGANIZATION_NOT_FOUND:
                    pass

        return result

    @override
    async def update(
        self,
        now: DateTime,
        id: OrganizationID,
        is_expired: UnsetType | bool = Unset,
        active_users_limit: UnsetType | ActiveUsersLimit = Unset,
        user_profile_outsider_allowed: UnsetType | bool = Unset,
        minimum_archiving_period: UnsetType | int = Unset,
        tos: UnsetType | None | dict[TosLocale, TosUrl] = Unset,
        allowed_client_agent: UnsetType | AllowedClientAgent = Unset,
        account_vault_strategy: UnsetType | AccountVaultStrategy = Unset,
    ) -> None | OrganizationUpdateBadOutcome:
        if minimum_archiving_period is not Unset:
            assert minimum_archiving_period >= 0  # Sanity check

        try:
            org = self._data.organizations[id]
        except KeyError:
            return OrganizationUpdateBadOutcome.ORGANIZATION_NOT_FOUND

        if is_expired is not Unset:
            org.is_expired = is_expired
        if active_users_limit is not Unset:
            org.active_users_limit = active_users_limit
        if user_profile_outsider_allowed is not Unset:
            org.user_profile_outsider_allowed = user_profile_outsider_allowed
        if minimum_archiving_period is not Unset:
            org.minimum_archiving_period = minimum_archiving_period
        if tos is not Unset:
            if tos is None:
                org.tos = None
            else:
                org.tos = TermsOfService(updated_on=now, per_locale_urls=tos)
        if allowed_client_agent is not Unset:
            org.allowed_client_agent = allowed_client_agent
        if account_vault_strategy is not Unset:
            org.account_vault_strategy = account_vault_strategy

        # TODO: the event is triggered even if the orga was already expired, is this okay ?
        if org.is_expired:
            await self._event_bus.send(EventOrganizationExpired(organization_id=id))

        if tos is not Unset:
            await self._event_bus.send(EventOrganizationTosUpdated(organization_id=id))

    @override
    async def get_tos(
        self, id: OrganizationID
    ) -> TermsOfService | None | OrganizationGetTosBadOutcome:
        try:
            org = self._data.organizations[id]
        except KeyError:
            return OrganizationGetTosBadOutcome.ORGANIZATION_NOT_FOUND

        if org.tos is None:
            return None

        return org.tos

    @override
    async def test_dump_organizations(
        self, skip_templates: bool = True
    ) -> dict[OrganizationID, OrganizationDump]:
        items = {}
        for org in self._data.organizations.values():
            if org.organization_id.str.endswith("Template") and skip_templates:
                continue

            org.active_users_limit
            items[org.organization_id] = OrganizationDump(
                organization_id=org.organization_id,
                bootstrap_token=org.bootstrap_token,
                is_bootstrapped=org.is_bootstrapped,
                is_expired=org.is_expired,
                active_users_limit=org.active_users_limit,
                user_profile_outsider_allowed=org.user_profile_outsider_allowed,
                minimum_archiving_period=org.minimum_archiving_period,
                tos=org.tos,
                allowed_client_agent=org.allowed_client_agent,
                account_vault_strategy=org.account_vault_strategy,
            )
        return items

    @override
    async def test_dump_topics(self, id: OrganizationID) -> OrganizationDumpTopics:
        try:
            org = self._data.organizations[id]
        except KeyError:
            raise RuntimeError("Organization not found")

        return OrganizationDumpTopics(
            common=org.per_topic_last_timestamp["common"],
            sequester=org.per_topic_last_timestamp.get("sequester"),
            realms={
                k[1]: v
                for k, v in org.per_topic_last_timestamp.items()
                if isinstance(k, tuple) and k[0] == "realm"
            },
            shamir_recovery=org.per_topic_last_timestamp.get("shamir_recovery"),
        )

    @override
    async def test_drop_organization(self, id: OrganizationID) -> None:
        self._data.organizations.pop(id, None)

    @override
    async def test_duplicate_organization(
        self, source_id: OrganizationID, target_id: OrganizationID
    ) -> None:
        duplicated_org = self._data.organizations[source_id].clone_as(target_id)
        self._data.organizations[target_id] = duplicated_org
