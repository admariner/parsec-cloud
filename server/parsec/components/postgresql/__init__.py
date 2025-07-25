# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS
from __future__ import annotations

from typing import TYPE_CHECKING

import asyncpg

if TYPE_CHECKING:
    # TODO: Replace with `type` once the linter supports it
    type AsyncpgConnection = asyncpg.Connection[asyncpg.Record]
    # TODO: Replace with `type` once the linter supports it
    type AsyncpgPool = asyncpg.Pool[asyncpg.Record]
else:
    # Asyncpg class are not subscriptable at runtime only during type checking (provided by `asyncpg-stubs`).
    AsyncpgConnection = asyncpg.Connection
    AsyncpgPool = asyncpg.Pool

# from parsec.components.postgresql.block import PGBlockComponent, PGBlockStoreComponent
from parsec.components.postgresql.factory import components_factory
from parsec.components.postgresql.handler import (
    MigrationItem,
    MigrationResult,
    apply_migrations,
    retrieve_migrations,
)
from parsec.components.postgresql.organization import PGOrganizationComponent
from parsec.components.postgresql.ping import PGPingComponent
from parsec.components.postgresql.pki import PGPkiEnrollmentComponent
from parsec.components.postgresql.realm import PGRealmComponent
from parsec.components.postgresql.user import PGUserComponent
from parsec.components.postgresql.vlob import PGVlobComponent

__all__ = [
    "MigrationItem",
    "MigrationResult",
    "PGOrganizationComponent",
    "PGPingComponent",
    "PGPkiEnrollmentComponent",
    "PGRealmComponent",
    "PGUserComponent",
    "PGVlobComponent",
    "apply_migrations",
    "components_factory",
    "retrieve_migrations",
]
