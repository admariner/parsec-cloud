# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS


from parsec._parsec import DateTime, InvitationType, authenticated_account_cmds
from tests.common import (
    AuthenticatedAccountRpcClient,
    Backend,
    CoolorgRpcClients,
    HttpCommonErrorsTester,
    MinimalorgRpcClients,
    ShamirOrgRpcClients,
    alice_gives_profile,
)


async def test_authenticated_account_invite_self_list_ok(
    backend: Backend,
    alice_account: AuthenticatedAccountRpcClient,
    bob_account: AuthenticatedAccountRpcClient,
    minimalorg: MinimalorgRpcClients,
    shamirorg: ShamirOrgRpcClients,
    coolorg: CoolorgRpcClients,
) -> None:
    def cook_and_compare(
        got: authenticated_account_cmds.latest.invite_self_list.Rep,
        expected: authenticated_account_cmds.latest.invite_self_list.Rep,
    ):
        if isinstance(got, authenticated_account_cmds.latest.invite_self_list.RepOk):
            to_keep_org_ids = (
                minimalorg.organization_id,
                shamirorg.organization_id,
                coolorg.organization_id,
            )
            cooked_got_invitations = sorted(
                # Only consider the organizations we know about, since there is also
                # template organizations and organizations created from previous tests.
                (x for x in got.invitations if x[0] in to_keep_org_ids),
                # Sort by org + invitation token
                key=lambda x: (x[0].str, x[1].bytes),
            )
            cooked_got = authenticated_account_cmds.latest.invite_self_list.RepOk(
                cooked_got_invitations
            )
        else:
            cooked_got = got

        if isinstance(expected, authenticated_account_cmds.latest.invite_self_list.RepOk):
            cooked_expected = authenticated_account_cmds.latest.invite_self_list.RepOk(
                sorted(expected.invitations, key=lambda x: (x[0].str, x[1].bytes))
            )
        else:
            cooked_expected = expected

        assert cooked_got == cooked_expected

    # Frozen should have no effect (but it is a common mistake to confuse it with revoked)
    await backend.user.freeze_user(
        coolorg.organization_id, user_id=coolorg.alice.user_id, user_email=None, frozen=True
    )

    # Bob has no invitation...

    rep = await bob_account.invite_self_list()
    cook_and_compare(rep, authenticated_account_cmds.latest.invite_self_list.RepOk(invitations=[]))

    # ... but Alice has plenty !

    rep = await alice_account.invite_self_list()
    cook_and_compare(
        rep,
        authenticated_account_cmds.latest.invite_self_list.RepOk(
            invitations=[
                (
                    shamirorg.organization_id,
                    shamirorg.shamir_invited_alice.token,
                    InvitationType.SHAMIR_RECOVERY,
                ),
                (coolorg.organization_id, coolorg.invited_alice_dev3.token, InvitationType.DEVICE),
            ]
        ),
    )

    # Now revoke Bob from CoolOrg and re-invite it to check user invitation

    assert bob_account.account_email == coolorg.bob.human_handle.email
    await alice_gives_profile(coolorg, backend, coolorg.bob.user_id, None)
    outcome = await backend.invite.new_for_user(
        DateTime.now(),
        coolorg.organization_id,
        coolorg.alice.device_id,
        bob_account.account_email,
        send_email=False,
    )
    assert isinstance(outcome, tuple)
    bob_invitation_token = outcome[0]

    rep = await bob_account.invite_self_list()
    cook_and_compare(
        rep,
        authenticated_account_cmds.latest.invite_self_list.RepOk(
            invitations=[(coolorg.organization_id, bob_invitation_token, InvitationType.USER)]
        ),
    )


async def test_authenticated_account_invite_self_list_http_common_errors(
    alice_account: AuthenticatedAccountRpcClient,
    authenticated_account_http_common_errors_tester: HttpCommonErrorsTester,
) -> None:
    async def do():
        await alice_account.invite_self_list()

    await authenticated_account_http_common_errors_tester(do)
