// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

use std::path::Path;

use crate::{load_available_device, load_device, save_device};
use libparsec_tests_fixtures::{tmp_path, TmpPath};
use libparsec_tests_lite::prelude::*;
use libparsec_types::prelude::*;

#[parsec_test]
#[case("password")]
#[cfg_attr(not(target_arch = "wasm32"), case("keyring"))]
#[case("account_vault")]
async fn save_load(#[case] kind: &str, tmp_path: TmpPath) {
    use crate::tests::utils::key_present_in_system;

    let key_file = tmp_path.join("devices/keyring_file.keys");
    let url = ParsecOrganizationAddr::from_any(
        // cspell:disable-next-line
        "parsec3://test.invalid/Org?no_ssl=true&p=xCD7SjlysFv3d4mTkRu-ZddRjIZPGraSjUnoOHT9s8rmLA",
    )
    .unwrap();
    let device = LocalDevice::generate_new_device(
        url,
        UserProfile::Admin,
        HumanHandle::from_raw("alice@dev1", "alice").unwrap(),
        "alice label".parse().unwrap(),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    );

    let (access, expected_available_device) = match kind {
        "keyring" => {
            let access = DeviceAccessStrategy::Keyring {
                key_file: key_file.clone(),
            };
            let expected_available_device = AvailableDevice {
                key_file_path: key_file.clone(),
                created_on: "2000-01-01T00:00:00Z".parse().unwrap(),
                protected_on: "2000-01-01T00:00:00Z".parse().unwrap(),
                server_url: "http://test.invalid/".to_string(),
                organization_id: device.organization_id().to_owned(),
                user_id: device.user_id,
                device_id: device.device_id,
                human_handle: device.human_handle.clone(),
                device_label: device.device_label.clone(),
                ty: AvailableDeviceType::Keyring,
            };
            (access, expected_available_device)
        }

        "password" => {
            let access = DeviceAccessStrategy::Password {
                key_file: key_file.clone(),
                password: "P@ssw0rd.".to_string().into(),
            };
            let expected_available_device = AvailableDevice {
                key_file_path: key_file.clone(),
                created_on: "2000-01-01T00:00:00Z".parse().unwrap(),
                protected_on: "2000-01-01T00:00:00Z".parse().unwrap(),
                server_url: "http://test.invalid/".to_string(),
                organization_id: device.organization_id().to_owned(),
                user_id: device.user_id,
                device_id: device.device_id,
                human_handle: device.human_handle.clone(),
                device_label: device.device_label.clone(),
                ty: AvailableDeviceType::Password,
            };
            (access, expected_available_device)
        }

        "account_vault" => {
            let ciphertext_key_id =
                AccountVaultItemOpaqueKeyID::from_hex("4ce154500ce340bcaa4d44dcb9b841a1").unwrap();
            let access = DeviceAccessStrategy::AccountVault {
                key_file: key_file.clone(),
                ciphertext_key_id,
                ciphertext_key: hex!(
                    "c102ac8b5c1cf2705711c00aec72a11bcd5f34b483ef25627e1c1f9ed6eefd76"
                )
                .into(),
            };
            let expected_available_device = AvailableDevice {
                key_file_path: key_file.clone(),
                created_on: "2000-01-01T00:00:00Z".parse().unwrap(),
                protected_on: "2000-01-01T00:00:00Z".parse().unwrap(),
                server_url: "http://test.invalid/".to_string(),
                organization_id: device.organization_id().to_owned(),
                user_id: device.user_id,
                device_id: device.device_id,
                human_handle: device.human_handle.clone(),
                device_label: device.device_label.clone(),
                ty: AvailableDeviceType::AccountVault { ciphertext_key_id },
            };
            (access, expected_available_device)
        }

        unknown => panic!("Unknown kind: {unknown:?}"),
    };

    assert!(!key_present_in_system(&key_file).await);

    device
        .time_provider
        .mock_time_frozen("2000-01-01T00:00:00Z".parse().unwrap());
    let available_device = save_device(&tmp_path, &access, &device).await.unwrap();
    device.time_provider.unmock_time();

    p_assert_eq!(available_device, expected_available_device);
    assert!(key_present_in_system(&key_file).await);

    let res = load_device(Path::new(""), &access).await.unwrap();

    p_assert_eq!(*res, device);

    // Also test `load_available_device`

    let available_device = load_available_device(Path::new(""), access.key_file().to_owned())
        .await
        .unwrap();
    p_assert_eq!(available_device, expected_available_device)
}
