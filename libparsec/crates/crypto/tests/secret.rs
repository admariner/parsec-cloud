// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

// `allow-unwrap-in-test` don't behave as expected, see:
// https://github.com/rust-lang/rust-clippy/issues/11119
#![allow(clippy::unwrap_used)]

use hex_literal::hex;
use pretty_assertions::assert_eq;
use rstest::rstest;
use serde_test::{assert_tokens, Token};

use libparsec_crypto::{CryptoError, SecretKey, SecretKeyPassphrase};

#[macro_use]
mod common;

#[test]
fn consts() {
    assert_eq!(SecretKey::ALGORITHM, "xsalsa20poly1305");
    assert_eq!(SecretKey::SIZE, 32);
}

test_serde!(serde, SecretKey);

#[test]
fn round_trip() {
    let sk = SecretKey::generate();

    let data = b"Hello, world !";
    let ciphered = sk.encrypt(data);

    let data2 = sk.decrypt(&ciphered).unwrap();
    assert_eq!(data2, data);
}

#[test]
fn bad_decrypt() {
    let sk = SecretKey::generate();

    assert_eq!(sk.decrypt(b""), Err(CryptoError::Nonce));

    assert_eq!(sk.decrypt(&[0; 64]), Err(CryptoError::Decryption));
}

#[test]
fn data_decrypt_spec() {
    let sk = SecretKey::from(hex!(
        "2ff13803789977db4f8ccabfb6b26f3e70eb4453d396dcb2315f7690cbc2e3f1"
    ));
    // Ciphertext generated with base python implementation
    let ciphertext = hex!(
        "5705b4386acf746e64aca52767d7fdd66bff3e82d87be3346c6d8e9c0ca0db43afe622"
        "c04473551737c2a0c65200bf64580c40f639ad6c622286ba13a92612ea2358d78f3b96"
    );
    let cleartext = sk.decrypt(&ciphertext).unwrap();
    assert_eq!(cleartext, b"all your base are belong to us");
}

test_msgpack_serialization!(
    secretkey_serialization_spec,
    SecretKey,
    hex!("856785fb1f72d3e2fdace29f02fbf8da9161cc84baec9669870f5c69fa5dc7e6"),
    hex!("c420856785fb1f72d3e2fdace29f02fbf8da9161cc84baec9669870f5c69fa5dc7e6")
);

#[test]
fn sas_code() {
    let sk = SecretKey::from(hex!(
        "2ff13803789977db4f8ccabfb6b26f3e70eb4453d396dcb2315f7690cbc2e3f1"
    ));
    let data = b"all your base are belong to us";
    let hmac = sk.sas_code(data);
    assert_eq!(hmac, hex!("a0f507f4be"));
}

#[test]
fn mac_512() {
    let sk = SecretKey::from(hex!(
        "2ff13803789977db4f8ccabfb6b26f3e70eb4453d396dcb2315f7690cbc2e3f1"
    ));
    let data = b"all your base are belong to us";
    let hmac = sk.mac_512(data);
    assert_eq!(hmac, hex!("37e763810a922d4ff377f648d2a92fbabc3dc1271fd343fc961b387a2817b493788eb928a8550bf2ba2512fac822046b9365c525e0627455de89c74758880066"));
}

#[test]
fn secret_key_should_verify_length_when_deserialize() {
    let data = hex!("c40564756d6d79");
    assert_eq!(
        rmp_serde::from_slice::<SecretKey>(&data)
            .unwrap_err()
            .to_string(),
        "Invalid key size: expected 32 bytes, got 5 bytes"
    );
}

#[rstest]
#[case::without_padding(0)]
#[case::with_half_padding(3)]
#[case::with_padding(6)]
fn recovery_passphrase(#[case] padding: usize) {
    let (passphrase, key) = SecretKey::generate_recovery_passphrase();

    let passphrase: SecretKeyPassphrase =
        format!("{}{}", passphrase.as_str(), "=".repeat(padding)).into();

    let key2 = SecretKey::from_recovery_passphrase(passphrase.clone()).unwrap();
    assert_eq!(key2, key);

    // Add dummy stuff to the passphrase should not cause issues
    let altered_passphrase = passphrase.to_lowercase().replace('-', "@  白");
    let key3 = SecretKey::from_recovery_passphrase(altered_passphrase.into()).unwrap();
    assert_eq!(key3, key);
}

#[rstest]
#[case::empty("", 0)]
#[case::only_invalid_characters("-@//白", 0)]
#[case::too_short("D5VR-53YO-QYJW-VJ4A-4DQR-4LVC-W425-3CXN-F3AQ-J6X2-YVPZ-XBAO", 30)]
#[case::too_long(
    "D5VR-53YO-QYJW-VJ4A-4DQR-4LVC-W425-3CXN-F3AQ-J6X2-YVPZ-XBAO-NU4Q-NU4Q",
    35
)]
fn invalid_passphrase(#[case] bad_passphrase: &str, #[case] key_length: usize) {
    assert_eq!(
        SecretKey::from_recovery_passphrase(bad_passphrase.to_owned().into()).unwrap_err(),
        CryptoError::KeySize {
            expected: SecretKey::SIZE,
            got: key_length,
        }
    );
}

#[test]
fn secretkey_from_too_small_data() {
    assert!(matches!(
        SecretKey::try_from(b"dummy".as_ref()),
        Err(CryptoError::KeySize { .. })
    ))
}

#[test]
fn encrypted_too_small() {
    let too_small = b"dummy";
    let sk = SecretKey::from(hex!(
        "2ff13803789977db4f8ccabfb6b26f3e70eb4453d396dcb2315f7690cbc2e3f1"
    ));

    assert!(matches!(sk.decrypt(too_small), Err(CryptoError::Nonce)));
}

#[test]
fn hash() {
    let sk1 = SecretKey::from(hex!(
        "2ff13803789977db4f8ccabfb6b26f3e70eb4453d396dcb2315f7690cbc2e3f1"
    ));
    let sk2 = SecretKey::from(hex!(
        "8f46e610b307443ec4ac81a4d799cbe1b97987901d4f681b82dacf3b59cad0a1"
    ));

    let hash = |x: &SecretKey| {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        x.hash(&mut hasher);
        hasher.finish()
    };

    assert_eq!(hash(&sk1), hash(&sk1));
    assert_ne!(hash(&sk1), hash(&sk2));
}
