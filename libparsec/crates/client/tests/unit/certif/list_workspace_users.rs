// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

use libparsec_tests_fixtures::prelude::*;
use libparsec_types::prelude::*;

use super::utils::certificates_ops_factory;

#[parsec_test(testbed = "minimal")]
async fn ok(env: &TestbedEnv) {
    let (env, realm_id) =
        env.customize_with_map(|builder| builder.new_realm("alice").map(|event| event.realm_id));
    let alice = env.local_device("alice@dev1");
    let ops = certificates_ops_factory(&env, &alice).await;

    ops.add_certificates_batch(
        &env.get_common_certificates_signed(),
        &[],
        &[],
        &env.get_realms_certificates_signed(),
    )
    .await
    .unwrap();

    let res = ops
        .list_workspace_users(realm_id)
        .await
        .unwrap()
        .into_iter()
        .map(|x| (x.user_id, x.current_profile, x.current_role))
        .collect::<Vec<_>>();

    p_assert_eq!(
        res,
        [(
            "alice".parse().unwrap(),
            UserProfile::Admin,
            RealmRole::Owner
        )]
    );
}

#[parsec_test(testbed = "minimal")]
async fn multiple(env: &TestbedEnv) {
    let (env, realm_id) = env.customize_with_map(|builder| {
        builder.new_user("bob");

        let realm_id = builder
            .new_realm("alice")
            .then_do_initial_key_rotation()
            .map(|event| event.realm);

        builder.share_realm(realm_id, "bob", RealmRole::Contributor);

        realm_id
    });
    let alice = env.local_device("alice@dev1");
    let ops = certificates_ops_factory(&env, &alice).await;

    ops.add_certificates_batch(
        &env.get_common_certificates_signed(),
        &[],
        &[],
        &env.get_realms_certificates_signed(),
    )
    .await
    .unwrap();

    let mut res = ops
        .list_workspace_users(realm_id)
        .await
        .unwrap()
        .into_iter()
        .map(|x| (x.user_id, x.current_profile, x.current_role))
        .collect::<Vec<_>>();

    // list_workspace_users is unstable
    res.sort_by(|x, y| x.0.cmp(&y.0));

    p_assert_eq!(
        res,
        [
            (
                "alice".parse().unwrap(),
                UserProfile::Admin,
                RealmRole::Owner
            ),
            (
                "bob".parse().unwrap(),
                UserProfile::Standard,
                RealmRole::Contributor
            ),
        ]
    );
}

#[parsec_test(testbed = "minimal")]
async fn empty(env: &TestbedEnv) {
    let alice = env.local_device("alice@dev1");
    let ops = certificates_ops_factory(env, &alice).await;

    let res = ops.list_workspace_users(VlobID::default()).await.unwrap();

    assert!(res.is_empty());
}