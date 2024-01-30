// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

use libparsec_tests_fixtures::prelude::*;

use super::utils::certificates_ops_factory;

#[parsec_test(testbed = "minimal")]
async fn ok(env: &TestbedEnv) {
    let alice = env.local_device("alice@dev1");
    let ops = certificates_ops_factory(env, &alice).await;

    ops.add_certificates_batch(
        &env.get_common_certificates_signed(),
        &[],
        &[],
        &Default::default(),
    )
    .await
    .unwrap();

    let res = ops
        .list_user_devices("alice".parse().unwrap())
        .await
        .unwrap()
        .into_iter()
        .map(|x| x.id)
        .collect::<Vec<_>>();

    p_assert_eq!(res, ["alice@dev1".parse().unwrap()]);
}

#[parsec_test(testbed = "minimal")]
async fn multiple(env: &TestbedEnv) {
    let env = env.customize(|builder| {
        builder.new_device("alice");
    });
    let alice = env.local_device("alice@dev1");
    let ops = certificates_ops_factory(&env, &alice).await;

    ops.add_certificates_batch(
        &env.get_common_certificates_signed(),
        &[],
        &[],
        &Default::default(),
    )
    .await
    .unwrap();

    let res = ops
        .list_user_devices("alice".parse().unwrap())
        .await
        .unwrap()
        .into_iter()
        .map(|x| x.id)
        .collect::<Vec<_>>();

    p_assert_eq!(
        res,
        ["alice@dev1".parse().unwrap(), "alice@dev2".parse().unwrap()]
    );
}

#[parsec_test(testbed = "minimal")]
async fn empty(env: &TestbedEnv) {
    let alice = env.local_device("alice@dev1");
    let ops = certificates_ops_factory(env, &alice).await;

    let res = ops
        .list_user_devices("alice".parse().unwrap())
        .await
        .unwrap();

    assert!(res.is_empty());
}