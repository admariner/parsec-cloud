# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

from unittest.mock import ANY

import pytest

from parsec._parsec import (
    DateTime,
    HashAlgorithm,
    RealmKeyRotationCertificate,
    SecretKeyAlgorithm,
    VlobID,
    authenticated_cmds,
    testbed,
)
from parsec.events import EventVlob
from tests.common import Backend, CoolorgRpcClients, get_last_realm_certificate_timestamp


@pytest.mark.parametrize("key_index", (0, 1))
async def test_authenticated_vlob_create_ok(
    key_index: int, coolorg: CoolorgRpcClients, backend: Backend
) -> None:
    vlob_id = VlobID.new()
    initial_dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)

    if key_index == 0:
        assert isinstance(coolorg.alice.event, testbed.TestbedEventBootstrapOrganization)
        realm_id = coolorg.alice.event.first_user_user_realm_id
        last_realm_certificate_timestamp = DateTime(2000, 1, 14)
    else:
        realm_id = coolorg.wksp1_id
        last_realm_certificate_timestamp = DateTime(2000, 1, 12)

    v1_blob = b"<block content>"
    v1_timestamp = DateTime.now()
    with backend.event_bus.spy() as spy:
        rep = await coolorg.alice.vlob_create(
            realm_id=realm_id,
            vlob_id=vlob_id,
            key_index=key_index,
            timestamp=v1_timestamp,
            blob=v1_blob,
            sequester_blob=None,
        )
        assert rep == authenticated_cmds.v4.vlob_create.RepOk()

        await spy.wait_event_occurred(
            EventVlob(
                organization_id=coolorg.organization_id,
                author=coolorg.alice.device_id,
                realm_id=realm_id,
                timestamp=v1_timestamp,
                vlob_id=vlob_id,
                version=1,
                blob=v1_blob,
                last_common_certificate_timestamp=DateTime(2000, 1, 6),
                last_realm_certificate_timestamp=last_realm_certificate_timestamp,
            )
        )

    dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)
    assert dump == {
        **initial_dump,
        vlob_id: [(coolorg.alice.device_id, ANY, realm_id, v1_blob)],
    }


async def test_authenticated_vlob_create_author_not_allowed(
    coolorg: CoolorgRpcClients, backend: Backend
) -> None:
    vlob_id = VlobID.new()

    initial_dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)

    rep = await coolorg.mallory.vlob_create(
        realm_id=coolorg.wksp1_id,
        vlob_id=vlob_id,
        key_index=1,
        timestamp=DateTime.now(),
        blob=b"<block content>",
        sequester_blob=None,
    )
    assert rep == authenticated_cmds.v4.vlob_create.RepAuthorNotAllowed()

    # Ensure no changes were made
    dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)
    assert dump == initial_dump


@pytest.mark.parametrize("kind", ("index_1_too_old", "index_0_too_old", "index_2_unknown"))
async def test_authenticated_vlob_create_bad_key_index(
    coolorg: CoolorgRpcClients, backend: Backend, kind: str
) -> None:
    vlob_id = VlobID.new()
    initial_dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)

    t0 = DateTime(2009, 12, 31)
    t1 = DateTime(2010, 1, 1)

    wksp1_last_certificate_timestamp = get_last_realm_certificate_timestamp(
        testbed_template=coolorg.testbed_template,
        realm_id=coolorg.wksp1_id,
    )

    match kind:
        case "index_1_too_old":
            certif = RealmKeyRotationCertificate(
                author=coolorg.alice.device_id,
                timestamp=t0,
                realm_id=coolorg.wksp1_id,
                key_index=2,
                encryption_algorithm=SecretKeyAlgorithm.XSALSA20_POLY1305,
                hash_algorithm=HashAlgorithm.SHA256,
                key_canary=b"<dummy canary>",
            )
            outcome = await backend.realm.rotate_key(
                now=t0,
                organization_id=coolorg.organization_id,
                author=coolorg.alice.device_id,
                realm_key_rotation_certificate=certif.dump_and_sign(coolorg.alice.signing_key),
                keys_bundle=b"<dummy keys bundle>",
                per_participant_keys_bundle_access={
                    coolorg.alice.user_id: b"<dummy alice keys bundle access>",
                    coolorg.bob.user_id: b"<dummy bob keys bundle access>",
                },
            )
            assert isinstance(outcome, RealmKeyRotationCertificate)
            bad_key_index = 1
            wksp1_last_certificate_timestamp = t0

        case "index_0_too_old":
            bad_key_index = 0

        case "index_2_unknown":
            bad_key_index = 2

        case unknown:
            assert False, unknown

    rep = await coolorg.alice.vlob_create(
        realm_id=coolorg.wksp1_id,
        vlob_id=vlob_id,
        key_index=bad_key_index,
        timestamp=t1,
        blob=b"<block content>",
        sequester_blob=None,
    )
    assert rep == authenticated_cmds.v4.vlob_create.RepBadKeyIndex(
        last_realm_certificate_timestamp=wksp1_last_certificate_timestamp
    )

    # Ensure no changes were made
    dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)
    assert dump == initial_dump


async def test_authenticated_vlob_create_realm_not_found(
    coolorg: CoolorgRpcClients, backend: Backend
) -> None:
    vlob_id = VlobID.new()

    initial_dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)

    rep = await coolorg.mallory.vlob_create(
        realm_id=VlobID.new(),
        vlob_id=vlob_id,
        key_index=1,
        timestamp=DateTime.now(),
        blob=b"<block content>",
        sequester_blob=None,
    )
    assert rep == authenticated_cmds.v4.vlob_create.RepRealmNotFound()

    # Ensure no changes were made
    dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)
    assert dump == initial_dump


async def test_authenticated_vlob_create_vlob_already_exists(
    coolorg: CoolorgRpcClients, backend: Backend
) -> None:
    t0 = DateTime(2009, 12, 31)
    vlob_id = VlobID.new()
    outcome = await backend.vlob.create(
        now=t0,
        organization_id=coolorg.organization_id,
        author=coolorg.alice.device_id,
        realm_id=coolorg.wksp1_id,
        vlob_id=vlob_id,
        key_index=1,
        blob=b"<block content 1>",
        timestamp=t0,
        sequester_blob=None,
    )
    assert outcome is None, outcome

    initial_dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)

    rep = await coolorg.alice.vlob_create(
        realm_id=coolorg.wksp1_id,
        vlob_id=vlob_id,
        key_index=1,
        timestamp=DateTime.now(),
        blob=b"<block content>",
        sequester_blob=None,
    )
    assert rep == authenticated_cmds.v4.vlob_create.RepVlobAlreadyExists()

    # Ensure no changes were made
    dump = await backend.vlob.test_dump_vlobs(organization_id=coolorg.organization_id)
    assert dump == initial_dump


# TODO: check that blob bigger than EVENT_VLOB_MAX_BLOB_SIZE doesn't get in the event