// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

// Functions using rstest parametrize ignores `#[warn(clippy::too_many_arguments)]`
// decorator, so we must do global ignore instead :(
#![allow(clippy::too_many_arguments)]

use std::{
    collections::{HashMap, HashSet},
    num::NonZeroU64,
};

use crate::fixtures::{alice, timestamp, Device};
use crate::prelude::*;
use libparsec_tests_lite::prelude::*;

type AliceLocalFolderManifest = Box<dyn FnOnce(&Device) -> (&'static [u8], LocalFolderManifest)>;
type AliceLocalUserManifest = Box<dyn FnOnce(&Device) -> (&'static [u8], LocalUserManifest)>;

#[rstest]
fn serde_local_file_manifest_ok(alice: &Device) {
    // Generated from Python implementation (Parsec v2.6.0+dev)
    // Content:
    //   type: "local_file_manifest"
    //   updated: ext(1, 1638618643.208821)
    //   base: {
    //     type: "file_manifest"
    //     author: "alice@dev1"
    //     timestamp: ext(1, 1638618643.208821)
    //     id: ext(2, hex!("87c6b5fd3b454c94bab51d6af1c6930b"))
    //     version: 42
    //     created: ext(1, 1638618643.208821)
    //     updated: ext(1, 1638618643.208821)
    //     blocks: [
    //       {
    //         id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
    //         digest: hex!("076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560")
    //         offset: 0
    //         size: 512
    //       }
    //       {
    //         id: ext(2, hex!("d7e3af6a03e1414db0f4682901e9aa4b"))
    //         digest: hex!("e37ce3b00a1f15b3de62029972345420b76313a885c6ccc6e3b5547857b3ecc6")
    //         offset: 512
    //         size: 188
    //       }
    //     ]
    //     blocksize: 512
    //     parent: ext(2, hex!("07748fbf67a646428427865fd730bf3e"))
    //     size: 700
    //   }
    //   blocks: [
    //     [
    //       {
    //         id: ext(2, hex!("ad67b6b5b9ad4653bf8e2b405bb6115f"))
    //         access: {
    //           id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
    //           digest: hex!("076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560")
    //           offset: 0
    //           size: 512
    //         }
    //         raw_offset: 0
    //         raw_size: 512
    //         start: 0
    //         stop: 250
    //       }
    //       {
    //         id: ext(2, hex!("2f99258022a94555b3109e81d34bdf97"))
    //         access: None
    //         raw_offset: 250
    //         raw_size: 250
    //         start: 0
    //         stop: 250
    //       }
    //     ]
    //   ]
    //   blocksize: 512
    //   need_sync: true
    //   size: 500
    let data = hex!(
        "a4c84fa2b11cbdf2f60a8da8c04c17fb2a23f854d6018f07d19ed6aff2e8d22c15f3c8"
        "402a318c53b21a9a12b9f3d7ede7080ed07bc93237ce18358962a3f10f4733e0502948"
        "83baaa9a4074696adfc8377f9590f0e94bc9f81d785a1d9d4f1ae631d43ae9e730fe2f"
        "90705ce3337c5bf993133504a507f9abeb428a70c4d26e86afd3b0b581067d8690b144"
        "e94e82c45ae08f79a9a7a91aa0d29eec3be9c3760deda111797428755a76950fd9d801"
        "931df08f815aa58afc355ef119e4e0efbebd66794327ff6823d84bbd2324f28fc84d26"
        "9ce07a5786395bf239ee45d0ca50c023f8e06f440521595b667507a1610cb42a4c61d2"
        "778134a0c86a399a8a18e688d814e9a416ba8160550ab517627bca81e40466e1c1c318"
        "468d20e9b0f6ba7ac58a3072e123ee807e66c75f770a78d85088cac2b0a4d2fc6103dc"
        "38518c08f9774053e9843576e0359e29b1d2ab2f01f9306c22841f2343c6cfa2e74378"
        "867ac7158459c30886bcfdb28111799e3683886776e6c9ca87e79bf1b77b86b75aac51"
        "99ca3523a5b5a28cc029e9ab2adfaa67352956efe7b727f7b6ad741c067679a07a59e3"
        "a80dfdf35f21329e0622d509ebb751cbb8ed07cbcbe305ffdd0257cfe7754d2c64716e"
        "0c2d0094b347efe79838c33b3675aac3a2388839c02af48ee0ec925fa22e8a261491d2"
        "89e1eb8acae69d2933ffe13ac9ab327ee4f34b2cb679d2c6e8fcf0e696e1b783b0152b"
        "d311ebca0f98f66e28ad4f65df7d8e28a1c82ebac3d7e1c4b9838b7ddbe785f72cf041"
        "2268b76d2a28b65df23bbc6480785ce1d083d5050af337efd352c43bdf062c4e083624"
        "7a72368396c0776afdd96a3dcbcd52ab63a84762a55c84386abe455ba4859414f1856b"
        "1ac07e419a279094e24dac07cd374b1a08706f296a6b00eb0bd95898ae073705206ae6"
        "da7e4495f6bf06ed49c56d77c2721e5014fabef7a3db98cceda96bf5615c2e"
    );
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    let key = SecretKey::from(hex!(
        "b1b52e16c1b46ab133c8bf576e82d26c887f1e9deae1af80043a258c36fcabf3"
    ));
    let expected = LocalFileManifest {
        updated: now,
        base: FileManifest {
            author: alice.device_id.to_owned(),
            timestamp: now,
            id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
            version: 42,
            created: now,
            updated: now,
            blocks: vec![
                BlockAccess {
                    id: BlockID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    digest: HashDigest::from(hex!(
                        "076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560"
                    )),
                    key: None,
                    offset: 0,
                    size: NonZeroU64::try_from(512).unwrap(),
                },
                BlockAccess {
                    id: BlockID::from_hex("d7e3af6a03e1414db0f4682901e9aa4b").unwrap(),
                    digest: HashDigest::from(hex!(
                        "e37ce3b00a1f15b3de62029972345420b76313a885c6ccc6e3b5547857b3ecc6"
                    )),
                    key: None,
                    offset: 512,
                    size: NonZeroU64::try_from(188).unwrap(),
                },
            ],
            blocksize: Blocksize::try_from(512).unwrap(),
            parent: VlobID::from_hex("07748fbf67a646428427865fd730bf3e").unwrap(),
            size: 700,
        },
        blocks: vec![vec![
            Chunk {
                id: ChunkID::from_hex("ad67b6b5b9ad4653bf8e2b405bb6115f").unwrap(),
                access: Some(BlockAccess {
                    id: BlockID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    digest: HashDigest::from(hex!(
                        "076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f3"
                        "6560"
                    )),
                    key: None,
                    offset: 0,
                    size: NonZeroU64::try_from(512).unwrap(),
                }),
                raw_offset: 0,
                raw_size: NonZeroU64::new(512).unwrap(),
                start: 0,
                stop: NonZeroU64::new(250).unwrap(),
            },
            Chunk {
                id: ChunkID::from_hex("2f99258022a94555b3109e81d34bdf97").unwrap(),
                access: None,
                raw_offset: 250,
                raw_size: NonZeroU64::new(250).unwrap(),
                start: 0,
                stop: NonZeroU64::new(250).unwrap(),
            },
        ]],
        blocksize: Blocksize::try_from(512).unwrap(),
        need_sync: true,
        size: 500,
    };

    let manifest = LocalFileManifest::decrypt_and_load(&data, &key).unwrap();

    p_assert_eq!(manifest, expected);

    // Also test serialization round trip
    let data2 = manifest.dump_and_encrypt(&key);
    // Note we cannot just compare with `data` due to encryption and keys order
    let manifest2 = LocalFileManifest::decrypt_and_load(&data2, &key).unwrap();

    p_assert_eq!(manifest2, expected);
}

#[rstest]
fn serde_local_file_manifest_legacy_pre_parsec_v3_0(alice: &Device) {
    // Generated from Python implementation (Parsec v2.6.0+dev)
    // Content:
    //   type: "local_file_manifest"
    //   updated: ext(1, 1638618643.208821)
    //   base: {
    //     type: "file_manifest"
    //     author: "alice@dev1"
    //     timestamp: ext(1, 1638618643.208821)
    //     id: ext(2, hex!("87c6b5fd3b454c94bab51d6af1c6930b"))
    //     version: 42
    //     created: ext(1, 1638618643.208821)
    //     updated: ext(1, 1638618643.208821)
    //     blocks: [
    //       {
    //         id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
    //         digest: hex!("076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560")
    //         key: hex!("6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57")
    //         offset: 0
    //         size: 512
    //       }
    //       {
    //         id: ext(2, hex!("d7e3af6a03e1414db0f4682901e9aa4b"))
    //         digest: hex!("e37ce3b00a1f15b3de62029972345420b76313a885c6ccc6e3b5547857b3ecc6")
    //         key: hex!("c21ed3aae92c648cb1b6df8be149ebc872247db0dbd37686ff2d075e2d7505cc")
    //         offset: 512
    //         size: 188
    //       }
    //     ]
    //     blocksize: 512
    //     parent: ext(2, hex!("07748fbf67a646428427865fd730bf3e"))
    //     size: 700
    //   }
    //   blocks: [
    //     [
    //       {
    //         id: ext(2, hex!("ad67b6b5b9ad4653bf8e2b405bb6115f"))
    //         access: {
    //           id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
    //           digest: hex!("076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560")
    //           key: hex!("6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57")
    //           offset: 0
    //           size: 512
    //         }
    //         raw_offset: 0
    //         raw_size: 512
    //         start: 0
    //         stop: 250
    //       }
    //       {
    //         id: ext(2, hex!("2f99258022a94555b3109e81d34bdf97"))
    //         access: None
    //         raw_offset: 250
    //         raw_size: 250
    //         start: 0
    //         stop: 250
    //       }
    //     ]
    //   ]
    //   blocksize: 512
    //   need_sync: true
    //   size: 500
    let data = hex!(
        "c450757c3d73e4286e1552494251bba10b8cab17c36960c544fad501577b580fe7da7f"
        "6159b5592db42601f13bcf268557de21f99fcf80b97dfe6b180834f791e84f7ce43347"
        "51c855ecc6881e14896f8fd0632fea01976009f913b78641dfc6b6c440fa9e49d2ddc3"
        "e1e0302b543a1c574cbac9c635721aa7ddf427fe9516894db53e9dfc62aeb1aff20bb0"
        "6c775ca6bf95310c546ba68680bd532dd8a00b923e675e16fd484d96d08e830fd1f217"
        "a8ffe919946b523d362375af13648b46abd2a48f6bf7175c899bfaa15653344689189c"
        "4eba626092f904d2604605ff994f45c90e36de0c78597fca533f38c1e8f66e09310922"
        "708345cc8fe4225860d45ec3a4ce11a0fb24953d25aedab9cffdb07e675a02cc0e41df"
        "25ee50fb6edcd2dddb58be6f65c6af628a46b1bcb079a8ea1c9399c4aaae0f665f7ac8"
        "42ececf91d0a739401d0635e3ebed48959e40498b4e3c32d963b6202a1e1d8e0c99fa6"
        "adfcf22626ba5de7d91326d88932a7f4df9c061099e69b212296b959e4d6a3cd58a4a6"
        "cc4bfc2b2a5b0f490f46fc36f7932eb585cd9ac765ce1e36730c72498c918514ccf091"
        "0f73bda2fea78bfb9cf90a5fe6b099efe95677ea253a6efbfc0d709d0badf6fe900434"
        "33f4a3e8699b747ed079cdff37358ececb0e84b5a597a3edd2c926d79bb17607d0fc41"
        "c35a5511f84d4b6cb168e5d384f96b86341440a9abe0f6682b148a1e4926d07f9e4088"
        "83788a21cf2ffd7dfb930fe26f8a46a4fee80bcbe425dded489dca9f3e7d45eec85154"
        "3f35bb1763e3f3a68a54d279b033617339ee9ab6da2db3fb79e5c62c90006ff3db702f"
        "4dc373debfafa3326fe3099768bae557c02837115249a21240af86d227d19c896672fb"
        "6fb729d8131837bfa086682a4299fc173a6b05ce025d8020488625df5931bb1696f068"
        "28d80c868394004b8de95423456a6cef1a8b1a2c9f5836d1a377757d2636c382cc9c6d"
        "86e0d7e4df3752f17e43f5c7e6697cdcf40263f21b9a741aa3dc04bde55e3ea4047f7b"
        "8137ab27fc5706b74e9691788ce3b3d9cc4230bbb5aea343fa0bd13706d002211cc16e"
        "29d598cef410851777d69068df1250f19518e735cd34f03af9"
    );
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    let key = SecretKey::from(hex!(
        "b1b52e16c1b46ab133c8bf576e82d26c887f1e9deae1af80043a258c36fcabf3"
    ));
    let expected = LocalFileManifest {
        updated: now,
        base: FileManifest {
            author: alice.device_id.to_owned(),
            timestamp: now,
            id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
            version: 42,
            created: now,
            updated: now,
            blocks: vec![
                BlockAccess {
                    id: BlockID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    digest: HashDigest::from(hex!(
                        "076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560"
                    )),
                    // In Parsec < v3, access block access has a dedicated key instead of a key index
                    key: Some(SecretKey::from(hex!(
                        "6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57"
                    ))),
                    offset: 0,
                    size: NonZeroU64::try_from(512).unwrap(),
                },
                BlockAccess {
                    id: BlockID::from_hex("d7e3af6a03e1414db0f4682901e9aa4b").unwrap(),
                    digest: HashDigest::from(hex!(
                        "e37ce3b00a1f15b3de62029972345420b76313a885c6ccc6e3b5547857b3ecc6"
                    )),
                    key: Some(SecretKey::from(hex!(
                        "c21ed3aae92c648cb1b6df8be149ebc872247db0dbd37686ff2d075e2d7505cc"
                    ))),
                    offset: 512,
                    size: NonZeroU64::try_from(188).unwrap(),
                },
            ],
            blocksize: Blocksize::try_from(512).unwrap(),
            parent: VlobID::from_hex("07748fbf67a646428427865fd730bf3e").unwrap(),
            size: 700,
        },
        blocks: vec![vec![
            Chunk {
                id: ChunkID::from_hex("ad67b6b5b9ad4653bf8e2b405bb6115f").unwrap(),
                access: Some(BlockAccess {
                    id: BlockID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    digest: HashDigest::from(hex!(
                        "076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f3"
                        "6560"
                    )),
                    key: Some(SecretKey::from(hex!(
                        "6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57"
                    ))),
                    offset: 0,
                    size: NonZeroU64::try_from(512).unwrap(),
                }),
                raw_offset: 0,
                raw_size: NonZeroU64::new(512).unwrap(),
                start: 0,
                stop: NonZeroU64::new(250).unwrap(),
            },
            Chunk {
                id: ChunkID::from_hex("2f99258022a94555b3109e81d34bdf97").unwrap(),
                access: None,
                raw_offset: 250,
                raw_size: NonZeroU64::new(250).unwrap(),
                start: 0,
                stop: NonZeroU64::new(250).unwrap(),
            },
        ]],
        blocksize: Blocksize::try_from(512).unwrap(),
        need_sync: true,
        size: 500,
    };

    let manifest = LocalFileManifest::decrypt_and_load(&data, &key).unwrap();

    p_assert_eq!(manifest, expected);

    // Also test serialization round trip
    let data2 = manifest.dump_and_encrypt(&key);
    // Note we cannot just compare with `data` due to encryption and keys order
    let manifest2 = LocalFileManifest::decrypt_and_load(&data2, &key).unwrap();

    p_assert_eq!(manifest2, expected);
}

#[rstest]
fn serde_local_file_manifest_invalid_blocksize() {
    // Generated from Python implementation (Parsec v2.6.0+dev)
    // Content:
    //   type: "local_file_manifest"
    //   updated: ext(1, 1638618643.208821)
    //   base: {
    //     type: "file_manifest"
    //     author: "alice@dev1"
    //     timestamp: ext(1, 1638618643.208821)
    //     id: ext(2, hex!("87c6b5fd3b454c94bab51d6af1c6930b"))
    //     version: 42
    //     created: ext(1, 1638618643.208821)
    //     updated: ext(1, 1638618643.208821)
    //     blocks: []
    //     blocksize: 512
    //     parent: ext(2, hex!("07748fbf67a646428427865fd730bf3e"))
    //     size: 700
    //   }
    //   blocks: []
    //   blocksize: 2
    //   need_sync: true
    //   size: 500
    let data = hex!(
        "9642b002d69dca6df364c5828c7308477aba91645175df36e2451798cce2a32b1b68f9"
        "138c24779a4cf009ec1ef21363db76b779e50aaade081b476c9423d033f615a159455c"
        "3f79f9baeac79059b3aeafda5bb25cf6394b50d1c487fc193740cf207bba4a98803d81"
        "c672f05ec2a07a88701972bb92cd17400ae25c28344619d5b504b13ff4898831485653"
        "b7b260e9622899ace85d4897c86b013e2eac1443f1dbd0d3792af7db872c7c4ddece26"
        "0fa55e24caeeb63b404a4a775d4ddcfc461b48d4b7773cdf83e0861020c754f51a972b"
        "ad16c73d5030b7a4f7c6136a0a8e8eb9664ac5c9b697fd4b693776a6dc6f5eb3b32373"
        "d5339c4848ed27cb62f622caffaa2a67c7a879e877030de49352b649a164902a9c2d74"
        "dd84fb84d45a47e811855d369c259bfaeb7ff946f60d66d48a"
    );

    let key = SecretKey::from(hex!(
        "b1b52e16c1b46ab133c8bf576e82d26c887f1e9deae1af80043a258c36fcabf3"
    ));

    let manifest = LocalFileManifest::decrypt_and_load(&data, &key);

    assert!(manifest.is_err());
}

#[rstest]
#[case::folder_manifest(Box::new(|alice: &Device| {
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    (
        // Generated from Parsec v3.0.0-b.6+dev
        // Content:
        //   type: "local_folder_manifest"
        //   updated: ext(1, 1638618643.208821)
        //   base: {
        //     type: "folder_manifest"
        //     author: "alice@dev1"
        //     timestamp: ext(1, 1638618643.208821)
        //     id: ext(2, hex!("87c6b5fd3b454c94bab51d6af1c6930b"))
        //     parent: ext(2, hex!("07748fbf67a646428427865fd730bf3e"))
        //     version: 42
        //     created: ext(1, 1638618643.208821)
        //     updated: ext(1, 1638618643.208821)
        //     children: {wksp1:ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))}
        //   }
        //   children: {wksp2:ext(2, hex!("d7e3af6a03e1414db0f4682901e9aa4b"))}
        //   local_confinement_points: [ext(2, hex!("d7e3af6a03e1414db0f4682901e9aa4b"))]
        //   remote_confinement_points: [ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))]
        //   need_sync: true
        //   speculative: false
        &hex!(
            "199d17c0df1c4158f7cf9de4ddac04fc469512e34c9d711d3bce7f0892df3864ef9827"
            "dd1af08207bfc6625619896bb5c8c0a7d2d85580f0e812aa295d0c6cb7f38925c22994"
            "a44b2ed2a2d7b6c993b9d5f16d4ebec4ddcd39f94853b025d7a2115a37c7be2b25550f"
            "d3c5a473ca393cf092b29e76d439f1cb0eed0e1c81aca267065b5f639befdc2f3fe02a"
            "e2008cc185937c7cd491d733135e8ae9d2409587f4cc053e39a9c203e64fd422e3f8b7"
            "a10c68505b378904524cfcb922817d9d37968607e9940aa488ace790d1d1f10e11b359"
            "61832935db003ed513fe3b9d139d355228d401a318ce1fa332088fdaaf1d8d8e39a729"
            "8cec0b5f7ca84530d906878458cfa7aefe538b96b2e8e0e7478cd7e55a9b75642f6def"
            "90d26a0acd21d0803c1895f89fc510bb451bb40f1c4a39cd8200066535e931530d3372"
            "faa9111e08daa13f51ccf6d055c74db7eb31acb1186b70f454adb11333cea3cb57c5fe"
            "166fba7dc830b8951a7c7a87065020d05637be6bb35bea78c89a6f9f8314234b221123"
            "61d6e0a72a8c37acd350d84a769a3cf1b5a11dc5a4b40271ce15aac2f0c234fe4e6516"
            "55ea09"
        )[..],
        LocalFolderManifest {
            updated: now,
            base: FolderManifest {
                author: alice.device_id.to_owned(),
                timestamp: now,
                id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
                parent: VlobID::from_hex("07748fbf67a646428427865fd730bf3e").unwrap(),
                version: 42,
                created: now,
                updated: now,
                children: HashMap::from([
                    ("wksp1".parse().unwrap(), VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap())
                ]),
            },
            children: HashMap::from([
                ("wksp2".parse().unwrap(), VlobID::from_hex("d7e3af6a03e1414db0f4682901e9aa4b").unwrap())
            ]),
            local_confinement_points: HashSet::from([VlobID::from_hex("d7e3af6a03e1414db0f4682901e9aa4b").unwrap()]),
            remote_confinement_points: HashSet::from([VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap()]),
            need_sync: true,
            speculative: false,
        }
    )
}))]
#[case::folder_manifest_speculative(Box::new(|alice: &Device| {
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    (
        // Generated from Parsec v3.0.0-b.6+dev
        // Content:
        //   type: "local_folder_manifest"
        //   updated: ext(1, 1638618643.208821)
        //   base: {
        //     type: "folder_manifest"
        //     author: "alice@dev1"
        //     timestamp: ext(1, 1638618643.208821)
        //     id: ext(2, hex!("87c6b5fd3b454c94bab51d6af1c6930b"))
        //     parent: ext(2, hex!("07748fbf67a646428427865fd730bf3e"))
        //     version: 0
        //     created: ext(1, 1638618643.208821)
        //     updated: ext(1, 1638618643.208821)
        //     children: {}
        //   }
        //   children: {}
        //   local_confinement_points: []
        //   remote_confinement_points: []
        //   need_sync: true
        //   speculative: true
        &hex!(
            "7dce0d23f47e8a33eae42311870f5f030aa2dafea63e695d4eec371105e4a5182d29a5"
            "0f0d667d187e760a36bd429f0df8440dddcfa983987d66e0d2ceeac1238a2d4c47d9a2"
            "e267ee70f6ea84bf48912d92bda0ca6a5a1030d6b9f6b8ad431fd6026e82f4ebb38102"
            "3744cc059cda4c4ee749868e2abd0d920e04c29edc2f2f596f6ba16f0c50a308028dd4"
            "69c4b1265745bc5f2c0355c41f2471d99fe82b081d0da2efff6c4c87ca938159393a10"
            "c2d0250772570caee3d0e63d9a0be05f6533a91740189038dba9b4fa80c867e068bd91"
            "da97c9c4f4d06aff2c74d94e19da4a605631993b71adde221a3c521a26e49ce1928f7e"
            "c38b86f9e6d2b22984eefeab64e42a0f6a83428aaf064a3f72ea8e50709323d36fcffe"
            "56e1f331b7a0eb5cadf4201b072241f9828ea74b01c3a805060e48198537f88d9bb9c5"
            "624260214381e8796b0dea5dda4d43054f250c9f43943953"
        )[..],
        LocalFolderManifest {
            updated: now,
            base: FolderManifest {
                author: alice.device_id.to_owned(),
                timestamp: now,
                id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
                parent: VlobID::from_hex("07748fbf67a646428427865fd730bf3e").unwrap(),
                version: 0,
                created: now,
                updated: now,
                children: HashMap::new(),
            },
            children: HashMap::new(),
            local_confinement_points: HashSet::new(),
            remote_confinement_points: HashSet::new(),
            need_sync: true,
            speculative: true,
        }
    )
}))]
fn serde_local_folder_manifest(
    alice: &Device,
    #[case] generate_data_and_expected: AliceLocalFolderManifest,
) {
    let (data, expected) = generate_data_and_expected(alice);
    let key = SecretKey::from(hex!(
        "b1b52e16c1b46ab133c8bf576e82d26c887f1e9deae1af80043a258c36fcabf3"
    ));

    println!("==========>{:?}", expected.dump_and_encrypt(&key));

    let manifest = LocalFolderManifest::decrypt_and_load(data, &key).unwrap();

    p_assert_eq!(manifest, expected);

    // Also test serialization round trip
    let data2 = manifest.dump_and_encrypt(&key);
    // Note we cannot just compare with `data` due to encryption and keys order
    let manifest2 = LocalFolderManifest::decrypt_and_load(&data2, &key).unwrap();

    p_assert_eq!(manifest2, expected);
}

#[rstest]
#[case::need_sync(Box::new(|alice: &Device| {
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    (
        // Generated from Rust implementation (Parsec v3.0.0-alpha)
        // Content:
        //   type: "local_user_manifest"
        //   updated: ext(1, 1638618643.208821)
        //   need_sync: true
        //   speculative: false
        //   workspaces: [
        //     {
        //       name: "wksp1"
        //       id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
        //       name_origin: {
        //         type: "CERTIFICATE",
        //         timestamp: ext(1, 1638618643.208821)
        //       }
        //       role: "CONTRIBUTOR"
        //       role_origin: {
        //         type: "CERTIFICATE",
        //         timestamp: ext(1, 1638618643.208821)
        //       }
        //     },
        //     {
        //       name: "wksp2"
        //       id: ext(2, hex!("d7e3af6a03e1414db0f4682901e9aa4b"))
        //       name_origin: {
        //         type: "PLACEHOLDER"
        //       }
        //       role: "CONTRIBUTOR"
        //       role_origin: {
        //         type: "PLACEHOLDER"
        //       }
        //     }
        //   ]
        //   base: {
        //     type: "user_manifest"
        //     author: "alice@dev1"
        //     timestamp: ext(1, 1638618643.208821)
        //     created: ext(1, 1638618643.208821)}
        //     updated: ext(1, 1638618643.208821)
        //     version: 42
        //   }
        &hex!(
            "dda242af1e4b65c1e2e3b858588faa1f7132b820d1cab62de4cb066956476551c57c5c"
            "9144183e4720ea536edad40c4878be651a74afa4b2d7153b1fe44fb3f882388a5df429"
            "95b7087b97d781d9cc8ae162d6187cdb6cc7e8942c1301e080e2cce588dd5a3e097f55"
            "1c77ac132119b6597d58f3ad499e51db4f312e8e65877188ad716987a073707f25d7a2"
            "bd58c6267f67b5316227b0ba18a261583de145a93708ac97dfe0d0e5dcb8715a11cded"
            "a022e76c20f2a4e7e5c190d7de5d2c7a3e08e8a15d65cdb1d3ef7a02ae1b55b35bdc6a"
            "178dd5a7819ea76f8002c73a2480f6c71de2aa163b5d8711111212d09b62468b464b92"
            "505ea6778eede30579a3d0158a9c2220f93ea6faec4472b89f91f5f676604c56e68d1f"
            "ee743b8dc7a691c7cd6d404132e4c79ba001f8c6baa3225e75ac1510471cdae5510dc6"
            "36ab526ba7b620c2a047836dfba8ab3ba6c99cab2ceb8c859fff86fc158028e95b87f4"
            "fe95669ddecd8d9c81be86e9f468aa6c3c936cfd8cb68e2914f51e0fd3c37e62ee6d66"
            "58e1f1e96bd6e4574588f30ef2c4b0b0736f3c0c760f387fcb9778b3468ddda3a14b59"
            "daf83c24c9005974ecb846f6515a347685db64fd18a263e92bafa9169d10b6b5937675"
            "0c725087b795a60a675c21da05acf14a3360a75db8a66c390d130f39972388a444292f"
            "295eb85b6d6c2bc610d44d6f0c0191b5cd1d0ef2acca3658b4dc27b820ba06"
        )[..],
        LocalUserManifest {
            updated: now,
            need_sync: true,
            speculative: false,
            base: UserManifest {
                author: alice.device_id.to_owned(),
                timestamp: now,
                id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
                version: 42,
                created: now,
                updated: now,
                workspaces_legacy_initial_info: vec![],
            },
            local_workspaces: vec![
                LocalUserManifestWorkspaceEntry {
                    name: "wksp1".parse().unwrap(),
                    id: VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    name_origin: CertificateBasedInfoOrigin::Certificate { timestamp: "2021-12-04T11:50:43.208821Z".parse().unwrap() },
                    role: RealmRole::Contributor,
                    role_origin: CertificateBasedInfoOrigin::Certificate { timestamp: "2021-12-04T11:50:43.208821Z".parse().unwrap() },
                },
                LocalUserManifestWorkspaceEntry {
                    name: "wksp2".parse().unwrap(),
                    id: VlobID::from_hex("d7e3af6a03e1414db0f4682901e9aa4b").unwrap(),
                    name_origin: CertificateBasedInfoOrigin::Placeholder,
                    role: RealmRole::Contributor,
                    role_origin: CertificateBasedInfoOrigin::Placeholder,
                },
            ],
        }
    )
}))]
#[case::synced(Box::new(|alice: &Device| {
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    (
        // Generated from Rust implementation (Parsec v3.0.0-alpha)
        // Content:
        //   type: "local_user_manifest"
        //   updated: ext(1, 1638618643.208821)
        //   need_sync: false
        //   speculative: false
        //   workspaces: [
        //     {
        //       name: "wksp1"
        //       id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
        //       name_origin: {
        //         type: "PLACEHOLDER"
        //       }
        //       role: "CONTRIBUTOR"
        //       role_origin: {
        //         type: "PLACEHOLDER"
        //       }
        //     },
        //   ]
        //   base: {
        //     type: "user_manifest"
        //     author: "alice@dev1"
        //     timestamp: ext(1, 1638618643.208821)
        //     id: ext(2, hex!("87c6b5fd3b454c94bab51d6af1c6930b"))
        //     version: 42
        //     created: ext(1, 1638618643.208821)}
        //     updated: ext(1, 1638618643.208821)
        //   }
        &hex!(
            "50010cba4177fab8462d492f50904a25ca9b4dab9ca438b3ceee4b60cc041d89778396"
            "8da007b2246b71f092f442763ad2caae31e2c15faedd534d30df64d4668fa966ce368d"
            "05bf6aff136dd4a245f17ebe0421518e2ae15b232b9bea8c2fc5d82247d928db9403f6"
            "adabc4a4a5e03b9bc041110ec02e1b3c527d1ffab2162d3b6320210b9bf79dff082603"
            "043732bb0b12cbb61b2d90935c073816877625759d5f9f489f6b26a485b60cc8cfff78"
            "a491e8a3c5d5ff2dd3b746e2afa58aa37fe85e52e15d045020ae24439a458c5a7aba70"
            "dccbd544fac9153cd7a6a40d9aff2492ec24dfe13f7afda8b63d4d7f31a20d94bfc03c"
            "cf4278d2a49f5a811f293b0e732b1b5e3ee79baf9c29c79e8dd75f1d9485ea8dfa73f4"
            "f5454b79baa4fb556f931ca8da9280b9624c46f1ab78f0f8c597d42483e362e8eb1121"
            "eacfdec9384f743b0da370bb4c147496c5206aa3d7fa5483e9d8a7ed3202fb9822814d"
            "1f6b6a05e2b56816fb8d29e386fd34a37b083db13c"
        )[..],
        LocalUserManifest {
            updated: now,
            need_sync: false,
            speculative: false,
            base: UserManifest {
                author: alice.device_id.to_owned(),
                timestamp: now,
                id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
                version: 42,
                created: now,
                updated: now,
                workspaces_legacy_initial_info: vec![],
            },
            local_workspaces: vec![
                LocalUserManifestWorkspaceEntry {
                    name: "wksp1".parse().unwrap(),
                    id: VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    name_origin: CertificateBasedInfoOrigin::Placeholder,
                    role: RealmRole::Contributor,
                    role_origin: CertificateBasedInfoOrigin::Placeholder,
                }
            ],
        }
    )
}))]
#[case::speculative(Box::new(|alice: &Device| {
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    (
        // Generated from Rust implementation (Parsec v3.0.0-alpha)
        // Content:
        //   type: "local_user_manifest"
        //   updated: ext(1, 1638618643.208821)
        //   need_sync: true
        //   speculative: true
        //   workspaces: []
        //   base: {
        //     type: "user_manifest"
        //     author: "alice@dev1"
        //     timestamp: ext(1, 1638618643.208821)
        //     id: ext(2, hex!("87c6b5fd3b454c94bab51d6af1c6930b"))
        //     version: 0
        //     created: ext(1, 1638618643.208821)
        //     updated: ext(1, 1638618643.208821)
        //   }
        &hex!(
            "9fed0982212a0cdeeb931d76ccc1e3cc45e70d6a0166ca366fd694031487f2f5187e45"
            "d99a55130b413f8953728ddcffca051b48b3d21487fa15c29977c5a4cdda91c34e13c6"
            "854eb122403b60d2cbd8799680178fbfcd990463fe11791a5c62b964d9b4f699bac938"
            "54494e06e1a848807f727039188c40246519076d626719f21e80bffeb61acdd60bd835"
            "d7941d3e9f18ea1af94e78e5380f086ee84f5be94e400d54cba65314fb9a0e02194d77"
            "43037bb0321e051e33653d3544d468d7cd2adb92aebb978170fc0e268d4bac3c5a960a"
            "22fb6015bc79e6338dc36b786f4e7d49b2d5a41b466a6afe4fca858b90c8e97407e85a"
            "acc575ec"
        )[..],
        LocalUserManifest {
            updated: now,
            need_sync: true,
            speculative: true,
            base: UserManifest {
                author: alice.device_id.to_owned(),
                timestamp: now,
                id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
                version: 0,
                created: now,
                updated: now,
                workspaces_legacy_initial_info: vec![],
            },
            local_workspaces: vec![],
        }
    )
}))]
#[case::legacy_pre_parsec_v3_0_need_sync(Box::new(|alice: &Device| {
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    (
        // Generated from Python implementation (Parsec v2.6.0)
        // Content:
        //   type: "local_user_manifest"
        //   updated: ext(1, 1638618643.208821)
        //   need_sync: true
        //   speculative: false
        //   last_processed_message: 4
        //   workspaces: [
        //     {
        //       name: "wksp1"
        //       id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
        //       role: "OWNER"
        //       key: hex!("6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57")
        //       encryption_revision: 2
        //       encrypted_on: ext(1, 1638618643.208821)
        //       role_cached_on: ext(1, 1638618643.208821)
        //     },
        //     {
        //       name: "wksp2"
        //       id: ext(2, hex!("d7e3af6a03e1414db0f4682901e9aa4b"))
        //       role: None
        //       key: hex!("c21ed3aae92c648cb1b6df8be149ebc872247db0dbd37686ff2d075e2d7505cc")
        //       encryption_revision: 1
        //       encrypted_on: ext(1, 1638618643.208821)
        //       role_cached_on: ext(1, 1638618643.208821)
        //     }
        //   ]
        //   base: {
        //     type: "user_manifest"
        //     author: "alice@dev1"
        //     timestamp: ext(1, 1638618643.208821)
        //     created: ext(1, 1638618643.208821)}
        //     updated: ext(1, 1638618643.208821)
        //     last_processed_message: 3
        //     version: 42
        //     workspaces: [
        //       {
        //         name: "wksp1"
        //         id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
        //         role: "OWNER"
        //         key: hex!("6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57")
        //         encryption_revision: 2
        //         encrypted_on: ext(1, 1638618643.208821)
        //         role_cached_on: ext(1, 1638618643.208821)
        //       }
        //     ]
        //   }
        &hex!(
            "ed02cad442320f04035cca2c094081b9995189a1645bc55568339a3a9233d91f8c31de"
            "e2c79890f0c474fb7a799deb0ad4b7ecd102453c33268354e79b612934517d599f8d53"
            "a61a93723dacae87922feb1a05ab987eb9922fcf751109e6ce279e38d09f6febbf3068"
            "b1bfd5390a13f90b90f8349e8e02e4714689317b96d1778e60735b14978f5e7e2663a2"
            "1a1e7b31018c1f0eb3a945b226e0aad02fdca5327b649faa04ad064cb34aa86d546453"
            "6878227a504d3a0ffa3217d364db018d7ea1cf3a24251582ca7f6de30e4feefbe40c09"
            "a6dbec96caca55c274043a685012c8272e981a2fa06fa4cdde2b5b0884a0ce45988869"
            "05b99e0148c5282e6021a57fcd4c043cd5744abe7ae0a504e616c7853db9df70c48579"
            "d084b88b36d485992d181578b467e7e6bdbb7417df43340548ac1a5b4a4e9f47461be9"
            "54de7d5e7fb3c9ede4a2abae3a0c4d130a34d213ad1efcd90747eb5280765c4a1e4a9f"
            "c8803bb889b5fa29e748b920c5b0ce1d88506e795a65a297682973735e83a59c345607"
            "a1066bf64ba08a2364750b6a8a8801b2e9f0a7309d08d66d8ef1fb69462845e63a51f9"
            "c9035cbf0443d60d3114a7390f8a9d58e69b2b94d8a7fdfb5437e3c516b33a3d07f81b"
            "b4d14d61522d437abd0e9979d63564555a6bfc8856d97233f5e28baf607b8944fe137e"
            "53eb956d78ca800721a6cd34e4f56f3d855e16be29580739b6fe03ac2ec806f27e8d87"
            "d83386a1fc3076526e62bf298b3a2d0ec6e441e08301e4b5a5f8aa72a5ca51aa3a6830"
            "64e20a735b531e40c3a3d3e26be61841cfa53b385aee36d899890b42d62a3710897527"
            "39effec2316199a358236bb12af40e0bf9111c8a1667002a1c1a1201df044a4f405bfa"
            "662e4a230b31bb12c44176489dafd34ad40ce121effe130eef81175b37f0eb8bff7520"
            "25b73a08470e5869e6c7b90e8a0c061cd66880ed90d6e57f09ff49ff4286ac82c33c7e"
            "cb75cd42abf37aa5abd4a7ef8bc406c022097f9271476503de00b476ccf3e750d9d242"
            "c49d7f6e3e940ef3704fdef14e33f7927786bc501f40"
        )[..],
        LocalUserManifest {
            updated: now,
            need_sync: true,
            speculative: false,
            // Local user manifest's `last_processed_message` field is deprecated (and hence ignored)
            base: UserManifest {
                author: alice.device_id.to_owned(),
                timestamp: now,
                id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
                version: 42,
                created: now,
                updated: now,
                workspaces_legacy_initial_info: vec![
                    LegacyUserManifestWorkspaceEntry {
                        name: "wksp1".parse().unwrap(),
                        id: VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                        key: SecretKey::from(hex!(
                            "6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57"
                        )),
                        encryption_revision: 2,
                        // Fields `encrypted_on/role_cache_timestamp/role_cache_value` are deprecated
                    }
                ],
                // User manifest's `last_processed_message` field is deprecated (and hence ignored)
            },
            local_workspaces: vec![
                LocalUserManifestWorkspaceEntry {
                    name: "wksp1".parse().unwrap(),
                    id: VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    name_origin: CertificateBasedInfoOrigin::Placeholder,
                    role: RealmRole::Owner,
                    role_origin: CertificateBasedInfoOrigin::Placeholder,
                    // Fields `key/encryption_revision/encrypted_on/role_cache_timestamp/role_cache_value` are deprecated
                }
            ],
        }
    )
}))]
#[case::legacy_pre_parsec_v3_0_synced(Box::new(|alice: &Device| {
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    (
        // Generated from Python implementation (Parsec v2.6.0)
        // Content:
        //   type: "local_user_manifest"
        //   updated: ext(1, 1638618643.208821)
        //   need_sync: false
        //   speculative: false
        //   last_processed_message: 3
        //   workspaces: [
        //     {
        //       name: "wksp1"
        //       id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
        //       role: "OWNER"
        //       key: hex!("6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57")
        //       encryption_revision: 2
        //       encrypted_on: ext(1, 1638618643.208821)
        //       role_cached_on: ext(1, 1638618643.208821)
        //     },
        //   ]
        //   base: {
        //     type: "user_manifest"
        //     author: "alice@dev1"
        //     timestamp: ext(1, 1638618643.208821)
        //     version: 42
        //     created: ext(1, 1638618643.208821)}
        //     updated: ext(1, 1638618643.208821)
        //     last_processed_message: 3
        //     workspaces: [
        //       {
        //         name: "wksp1"
        //         id: ext(2, hex!("b82954f1138b4d719b7f5bd78915d20f"))
        //         role: "OWNER"
        //         key: hex!("6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57")
        //         encryption_revision: 2
        //         encrypted_on: ext(1, 1638618643.208821)
        //         role_cached_on: ext(1, 1638618643.208821)
        //       }
        //     ]
        //   }
        &hex!(
            "07d50897a2530d094f195290dda1e120b6ca52e050aedb0d04dddc5f8d3886751cbdd6"
            "2d86928c1052f8317ff32667efdf380fa12f4da793d874d15f0ace61d48df2ab981aaf"
            "fb7041d704fb61f0c540e1e3f7056809a31f499e32a6078be256b40cf0713984bd4040"
            "cbbe8f15aad594a2f9e0dc9de8b1a354166331532e25b579ee4c84aceee9508877c0be"
            "5b6a74178e74c1b54033793b6699540acea85d2bddaf6abf5f8ca8609670b3780994cb"
            "b408e33daf665f1c872c33fecc799e64688ba9601c61c6fc90d5645a9fbbd0cbf26d65"
            "3b1c7ca67c3e9cf43a89597dac825bffd8ae7556d8409442e88ee01a92bd7c4bf24a0a"
            "6b7756f30b2e5a1d5f26925c7c8798bd9e48866c2b55de12a1fd4a3f1b89168c90b743"
            "50ae3c13a4660c999d835b75b6f043edbd961110b85babfc3bf442c1f780d0c8927376"
            "681a36c8e96763429e22f280a59aecf611f008c96a4fc2d8dd56699217b768d7dcd422"
            "62672f73a16b70946748b4b7b18d2976571014f5a652a1c12749e0255e7052535b4bf8"
            "38052ab0546cc77796d9ad45db19bc1eed127642316f0d60c926b93d97f865959dcc29"
            "7ba924c9b18fe0c091b4178183b0ec9af70cdfbf26625fef13e8924cf54db0f625973c"
            "b1933db92fdc1afb52ffce1261e6b66d2f383f88b877f73d40f6606b3a8d36a5323793"
            "d149c3d731fe3f86c0e1760966a4f4b5f5f2033178a6f9168999e6b358fa7879891e32"
            "3aba8076e0a978cba6d5a9d6edc235184065f9a385a967547b4cfacf5efc28acfb004e"
            "86194a9f9402a423bf21469821ee00ff0a28ab90bfc150682e0ca430987c9dc900aac5"
            "7a581b7420073bef892a066f35c4f5f0"
        )[..],
        LocalUserManifest {
            updated: now,
            need_sync: false,
            speculative: false,
            // Local user manifest's `last_processed_message` field is deprecated (and hence ignored)
            base: UserManifest {
                author: alice.device_id.to_owned(),
                timestamp: now,
                id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
                version: 42,
                created: now,
                updated: now,
                workspaces_legacy_initial_info: vec![
                    LegacyUserManifestWorkspaceEntry {
                        name: "wksp1".parse().unwrap(),
                        id: VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                        key: SecretKey::from(hex!(
                            "6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57"
                        )),
                        encryption_revision: 2,
                    }
                ],
                // User manifest's `last_processed_message` field is deprecated (and hence ignored)
            },
            local_workspaces: vec![
                LocalUserManifestWorkspaceEntry {
                    name: "wksp1".parse().unwrap(),
                    id: VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    name_origin: CertificateBasedInfoOrigin::Placeholder,
                    role: RealmRole::Owner,
                    role_origin: CertificateBasedInfoOrigin::Placeholder,
                    // Fields `key/encryption_revision/encrypted_on/role_cache_timestamp/role_cache_value` are deprecated
                }
            ],
        }
    )
}))]
#[case::legacy_pre_parsec_v3_0_speculative(Box::new(|alice: &Device| {
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    (
        // Generated from Python implementation (Parsec v2.6.0)
        // Content:
        //   type: "local_user_manifest"
        //   updated: ext(1, 1638618643.208821)
        //   need_sync: true
        //   speculative: true
        //   last_processed_message: 0
        //   workspaces: []
        //   base: {
        //     type: "user_manifest"
        //     author: "alice@dev1"
        //     timestamp: ext(1, 1638618643.208821)
        //     id: ext(2, hex!("87c6b5fd3b454c94bab51d6af1c6930b"))
        //     version: 0
        //     created: ext(1, 1638618643.208821)}
        //     updated: ext(1, 1638618643.208821)
        //     last_processed_message: 0
        //     workspaces: []
        //   }
        &hex!(
            "ce0274b3890ec74dff002d7b587e591ba4876b7f08fa227eb1ba737f6eae2490c79c1b"
            "e9c6211179274ce62439caeea5829c9265e46371fb6e198f3d13ef5e366e11653a64f0"
            "49941a1b6c70ba424019f7e09bcab7f53872cc3d65a9f23b71ec85b2f5b4524f58a035"
            "28ccf335af198e87fc1f1675da3473bd6a43804b4177267c9ba55c1ec955f5068de167"
            "6f9f8731ea4932a0c55c7eb3741893a5ce7e2c4f20406485821e964b7cf46442338c63"
            "771883da9d90098c1fea73339fa97aba3145977114b5f4c05d3b21733d3a9f476e7abf"
            "90602bc7b538ac7794e96e76c279e236e80564790efc67e61d8196cd4ba1806b763607"
            "0976bf4306be2f51fa705cbaa423890ba6a40b5b33ac75f71dd2a8e1bc93532a3bbee6"
            "59da075245905b5c46583e0479e8c60060e0e8bfaa94af4c32a201f6b0"
        )[..],
        LocalUserManifest {
            updated: now,
            need_sync: true,
            speculative: true,
            // Local user manifest's `last_processed_message` field is deprecated (and hence ignored)
            base: UserManifest {
                author: alice.device_id.to_owned(),
                timestamp: now,
                id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
                version: 0,
                created: now,
                updated: now,
                workspaces_legacy_initial_info: vec![],
                // User manifest's `last_processed_message` field is deprecated (and hence ignored)
            },
            local_workspaces: vec![],
        }
    )
}))]
#[case::legacy_pre_parsec_v1_15_missing_speculative_field(Box::new(|alice: &Device| {
    let now = "2021-12-04T11:50:43.208821Z".parse().unwrap();
    (
        // Generated from Python implementation (Parsec v2.6.0)
        // Content:
        //   type: "local_user_manifest"
        //   updated: ext(1, 1638618643.208821)
        //   need_sync: false
        //   last_processed_message: 0
        //   workspaces: []
        //   base: {
        //       type: "user_manifest"
        //       author: str(alice.device_id)
        //       timestamp: ext(1, 1638618643.208821)
        //       id: ext(2, hex!("87c6b5fd3b454c94bab51d6af1c6930b"))
        //       version: 0
        //       created: ext(1, 1638618643.208821)
        //       updated: ext(1, 1638618643.208821)
        //       last_processed_message: 0
        //       workspaces: []
        //   }
        &hex!(
            "7d38802a10c9b998d3cf460a48792a305113398fda609eb88ed2dbc40ad51098a5847e"
            "50a58f69bc374fba586d0b60cbc686819e4ae7d1507ed333d5f63caffae84ec5acf40e"
            "c7302c0c62e75407b0820fdcf1f8211143ba0415074033b37b4d6d136a7ba956c4fb0e"
            "046499822d377d5a82e3155537db73e58c48adbd5ed41abc4d7498c72947219b49ce6d"
            "e396beb42cef2f037e234792cebe3e46726b471ad3d0a1020a1f9d814d359b8763cb86"
            "992578c81e4c5f47d52333694e5df74f303a99c3b744ef0c942074aacf695d4e6eb389"
            "52a1ec9b2a414e6a00f2924dc4af0c349b0fc959a4422b6a92b7f9233403f71b1cb9bd"
            "6d367bf336b8acbc4eb82bfdacf948272fe53b3ecec4f06be968149c597f1e6afd529c"
            "2ece0410ec7cb6042e3eedf966c7248c"
        )[..],
        LocalUserManifest {
            updated: now,
            need_sync: false,
            speculative: false,
            // Local user manifest's `last_processed_message` field is deprecated (and hence ignored)
            local_workspaces: vec![],
            base: UserManifest {
                author: alice.device_id.to_owned(),
                timestamp: now,
                id: VlobID::from_hex("87c6b5fd3b454c94bab51d6af1c6930b").unwrap(),
                version: 0,
                created: now,
                updated: now,
                workspaces_legacy_initial_info: vec![],
                // User manifest's `last_processed_message` field is deprecated (and hence ignored)
            },
        }
    )
}))]
fn serde_local_user_manifest(
    alice: &Device,
    #[case] generate_data_and_expected: AliceLocalUserManifest,
) {
    let (data, expected) = generate_data_and_expected(alice);
    let key = SecretKey::from(hex!(
        "b1b52e16c1b46ab133c8bf576e82d26c887f1e9deae1af80043a258c36fcabf3"
    ));

    let manifest = LocalUserManifest::decrypt_and_load(data, &key).unwrap();

    p_assert_eq!(manifest, expected);

    // Also test serialization round trip
    let data2 = manifest.dump_and_encrypt(&key);
    // Note we cannot just compare with `data` due to encryption and keys order
    let manifest2 = LocalUserManifest::decrypt_and_load(&data2, &key).unwrap();

    p_assert_eq!(manifest2, expected);
}

#[rstest]
fn chunk_new() {
    let chunk = Chunk::new(1, NonZeroU64::try_from(5).unwrap());

    p_assert_eq!(chunk.start, 1);
    p_assert_eq!(chunk.stop, NonZeroU64::try_from(5).unwrap());
    p_assert_eq!(chunk.raw_offset, 1);
    p_assert_eq!(chunk.raw_size, NonZeroU64::try_from(4).unwrap());
    p_assert_eq!(chunk.access, None);

    p_assert_eq!(chunk, 1);
    assert!(chunk < 2);
    assert!(chunk > 0);
    p_assert_ne!(chunk, Chunk::new(1, NonZeroU64::try_from(5).unwrap()));
}

#[rstest]
fn chunk_promote_as_block() {
    let chunk = Chunk::new(1, NonZeroU64::try_from(5).unwrap());
    let id = chunk.id;
    let block = {
        let mut block = chunk.clone();
        block.promote_as_block(b"<data>").unwrap();
        block
    };

    p_assert_eq!(block.id, id);
    p_assert_eq!(block.start, 1);
    p_assert_eq!(block.stop, NonZeroU64::try_from(5).unwrap());
    p_assert_eq!(block.raw_offset, 1);
    p_assert_eq!(block.raw_size, NonZeroU64::try_from(4).unwrap());
    p_assert_eq!(*block.access.as_ref().unwrap().id, *id);
    p_assert_eq!(block.access.as_ref().unwrap().offset, 1);
    p_assert_eq!(block.access.as_ref().unwrap().key, None);
    p_assert_eq!(
        block.access.as_ref().unwrap().size,
        NonZeroU64::try_from(4).unwrap()
    );
    p_assert_eq!(
        block.access.as_ref().unwrap().digest,
        HashDigest::from_data(b"<data>")
    );

    let block_access = BlockAccess {
        id: BlockID::default(),
        key: None,
        offset: 1,
        size: NonZeroU64::try_from(4).unwrap(),
        digest: HashDigest::from_data(b"<data>"),
    };

    let mut block = Chunk::from_block_access(block_access);
    let err = block.promote_as_block(b"<data>").unwrap_err();
    p_assert_eq!(err, "already a block");

    let mut chunk = Chunk {
        id,
        start: 0,
        stop: NonZeroU64::try_from(1).unwrap(),
        raw_offset: 1,
        raw_size: NonZeroU64::try_from(1).unwrap(),
        access: None,
    };

    let err = chunk.promote_as_block(b"<data>").unwrap_err();
    p_assert_eq!(err, "not aligned");
}

#[rstest]
fn chunk_is_block() {
    let chunk = Chunk {
        id: ChunkID::default(),
        start: 0,
        stop: NonZeroU64::try_from(1).unwrap(),
        raw_offset: 0,
        raw_size: NonZeroU64::try_from(1).unwrap(),
        access: None,
    };

    assert!(chunk.is_pseudo_block());
    assert!(!chunk.is_block());

    let mut block = {
        let mut block = chunk.clone();
        block.promote_as_block(b"<data>").unwrap();
        block
    };

    assert!(block.is_pseudo_block());
    assert!(block.is_block());

    block.start = 1;

    assert!(!block.is_pseudo_block());
    assert!(!block.is_block());

    block.access.as_mut().unwrap().offset = 1;

    assert!(!block.is_pseudo_block());
    assert!(!block.is_block());

    block.raw_offset = 1;

    assert!(!block.is_pseudo_block());
    assert!(!block.is_block());

    block.stop = NonZeroU64::try_from(2).unwrap();

    assert!(block.is_pseudo_block());
    assert!(block.is_block());

    block.stop = NonZeroU64::try_from(5).unwrap();

    assert!(!block.is_pseudo_block());
    assert!(!block.is_block());

    block.raw_size = NonZeroU64::try_from(4).unwrap();

    assert!(block.is_pseudo_block());
    assert!(!block.is_block());

    block.access.as_mut().unwrap().size = NonZeroU64::try_from(4).unwrap();

    assert!(block.is_pseudo_block());
    assert!(block.is_block());
}

#[rstest]
fn local_file_manifest_new(timestamp: DateTime) {
    let author = DeviceID::default();
    let parent = VlobID::default();
    let lfm = LocalFileManifest::new(author.clone(), parent, timestamp);

    p_assert_eq!(lfm.base.author, author);
    p_assert_eq!(lfm.base.timestamp, timestamp);
    p_assert_eq!(lfm.base.parent, parent);
    p_assert_eq!(lfm.base.version, 0);
    p_assert_eq!(lfm.base.created, timestamp);
    p_assert_eq!(lfm.base.updated, timestamp);
    p_assert_eq!(lfm.base.blocksize, Blocksize::try_from(512 * 1024).unwrap());
    p_assert_eq!(lfm.base.size, 0);
    p_assert_eq!(lfm.base.blocks.len(), 0);
    assert!(lfm.need_sync);
    p_assert_eq!(lfm.updated, timestamp);
    p_assert_eq!(lfm.blocksize, Blocksize::try_from(512 * 1024).unwrap());
    p_assert_eq!(lfm.size, 0);
    p_assert_eq!(lfm.blocks.len(), 0);
}

#[rstest]
fn local_file_manifest_is_reshaped(timestamp: DateTime) {
    let author = DeviceID::default();
    let parent = VlobID::default();
    let mut lfm = LocalFileManifest::new(author, parent, timestamp);

    assert!(lfm.is_reshaped());

    let block = {
        let mut block = Chunk {
            id: ChunkID::default(),
            start: 0,
            stop: NonZeroU64::try_from(1).unwrap(),
            raw_offset: 0,
            raw_size: NonZeroU64::try_from(1).unwrap(),
            access: None,
        };
        block.promote_as_block(b"<data>").unwrap();
        block
    };

    lfm.blocks.push(vec![block.clone()]);

    assert!(lfm.is_reshaped());

    lfm.blocks[0].push(block);

    assert!(!lfm.is_reshaped());

    lfm.blocks[0].pop();
    lfm.blocks[0][0].access = None;

    assert!(!lfm.is_reshaped());
}

#[rstest]
#[case::empty((0, vec![]))]
#[case::blocks((1024, vec![
    BlockAccess {
        id: BlockID::default(),
        key: None,
        offset: 1,
        size: NonZeroU64::try_from(4).unwrap(),
        digest: HashDigest::from_data(&[]),
    },
    BlockAccess {
        id: BlockID::default(),
        key: None,
        offset: 513,
        size: NonZeroU64::try_from(4).unwrap(),
        digest: HashDigest::from_data(&[]),
    }
]))]
fn local_file_manifest_from_remote(timestamp: DateTime, #[case] input: (u64, Vec<BlockAccess>)) {
    let (size, blocks) = input;
    let fm = FileManifest {
        author: DeviceID::default(),
        timestamp,
        id: VlobID::default(),
        parent: VlobID::default(),
        version: 0,
        created: timestamp,
        updated: timestamp,
        size,
        blocksize: Blocksize::try_from(512).unwrap(),
        blocks: blocks.clone(),
    };

    let lfm = LocalFileManifest::from_remote(fm.clone());

    p_assert_eq!(lfm.base, fm);
    assert!(!lfm.need_sync);
    p_assert_eq!(lfm.updated, timestamp);
    p_assert_eq!(lfm.size, size);
    p_assert_eq!(lfm.blocksize, Blocksize::try_from(512).unwrap());
    p_assert_eq!(
        lfm.blocks,
        blocks
            .into_iter()
            .map(|block| vec![Chunk::from_block_access(block)])
            .collect::<Vec<_>>()
    );
}

#[rstest]
fn local_file_manifest_to_remote(timestamp: DateTime) {
    let t1 = timestamp;
    let t2 = t1.add_us(1);
    let t3 = t2.add_us(1);
    let author = DeviceID::default();
    let parent = VlobID::default();
    let mut lfm = LocalFileManifest::new(author, parent, t1);

    let block = {
        let mut block = Chunk {
            id: ChunkID::default(),
            start: 0,
            stop: NonZeroU64::try_from(1).unwrap(),
            raw_offset: 0,
            raw_size: NonZeroU64::try_from(1).unwrap(),
            access: None,
        };
        block.promote_as_block(b"<data>").unwrap();
        block
    };

    let block_access = block.access.clone().unwrap();
    lfm.blocks.push(vec![block]);
    lfm.size = 1;
    lfm.updated = t2;

    let author = DeviceID::default();
    let fm = lfm.to_remote(author.clone(), t3).unwrap();

    p_assert_eq!(fm.author, author);
    p_assert_eq!(fm.timestamp, t3);
    p_assert_eq!(fm.id, lfm.base.id);
    p_assert_eq!(fm.parent, lfm.base.parent);
    p_assert_eq!(fm.version, lfm.base.version + 1);
    p_assert_eq!(fm.created, lfm.base.created);
    p_assert_eq!(fm.updated, lfm.updated);
    p_assert_eq!(fm.size, lfm.size);
    p_assert_eq!(fm.blocksize, lfm.blocksize);
    p_assert_eq!(fm.blocks, vec![block_access]);
}

#[rstest]
fn local_file_manifest_match_remote(timestamp: DateTime) {
    let fm = FileManifest {
        author: DeviceID::default(),
        timestamp,
        id: VlobID::default(),
        parent: VlobID::default(),
        version: 0,
        created: timestamp,
        updated: timestamp,
        size: 1,
        blocksize: Blocksize::try_from(512).unwrap(),
        blocks: vec![BlockAccess {
            id: BlockID::default(),
            key: None,
            offset: 0,
            size: NonZeroU64::try_from(1).unwrap(),
            digest: HashDigest::from_data(&[]),
        }],
    };

    let lfm = LocalFileManifest {
        base: fm.clone(),
        need_sync: false,
        updated: timestamp,
        size: fm.size,
        blocksize: fm.blocksize,
        blocks: vec![vec![Chunk {
            id: ChunkID::default(),
            start: 0,
            stop: NonZeroU64::try_from(1).unwrap(),
            raw_offset: 0,
            raw_size: NonZeroU64::try_from(1).unwrap(),
            access: Some(fm.blocks[0].clone()),
        }]],
    };

    assert!(lfm.match_remote(&fm));
}

#[rstest]
fn local_folder_manifest_new(timestamp: DateTime) {
    let author = DeviceID::default();
    let parent = VlobID::default();
    let lfm = LocalFolderManifest::new(author.clone(), parent, timestamp);

    p_assert_eq!(lfm.base.author, author);
    p_assert_eq!(lfm.base.timestamp, timestamp);
    p_assert_eq!(lfm.base.parent, parent);
    p_assert_eq!(lfm.base.version, 0);
    p_assert_eq!(lfm.base.created, timestamp);
    p_assert_eq!(lfm.base.updated, timestamp);
    assert!(lfm.need_sync);
    p_assert_eq!(lfm.updated, timestamp);
    p_assert_eq!(lfm.children.len(), 0);
    p_assert_eq!(lfm.local_confinement_points.len(), 0);
    p_assert_eq!(lfm.remote_confinement_points.len(), 0);
    assert!(!lfm.speculative);
}

#[rstest]
fn local_folder_manifest_new_root(timestamp: DateTime) {
    let author = DeviceID::default();
    let realm = VlobID::default();
    let lfm = LocalFolderManifest::new_root(author.clone(), realm, timestamp, true);

    p_assert_eq!(lfm.base.author, author);
    p_assert_eq!(lfm.base.timestamp, timestamp);
    p_assert_eq!(lfm.base.id, realm);
    p_assert_eq!(lfm.base.parent, realm);
    p_assert_eq!(lfm.base.version, 0);
    p_assert_eq!(lfm.base.created, timestamp);
    p_assert_eq!(lfm.base.updated, timestamp);
    assert!(lfm.need_sync);
    p_assert_eq!(lfm.updated, timestamp);
    p_assert_eq!(lfm.children.len(), 0);
    p_assert_eq!(lfm.local_confinement_points.len(), 0);
    p_assert_eq!(lfm.remote_confinement_points.len(), 0);
    assert!(lfm.speculative);
}

#[rstest]
#[case::empty((
    HashMap::new(),
    HashMap::new(),
    0,
    "",
))]
#[case::children_filtered((
    HashMap::from([
        ("file1.png".parse().unwrap(), VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap())
    ]),
    HashMap::new(),
    1,
    ".+",
))]
#[case::children((
    HashMap::from([
        ("file1.png".parse().unwrap(), VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap())
    ]),
    HashMap::from([
        ("file1.png".parse().unwrap(), VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap())
    ]),
    0,
    ".mp4",
))]
fn local_folder_manifest_from_remote(
    timestamp: DateTime,
    #[case] input: (
        HashMap<EntryName, VlobID>,
        HashMap<EntryName, VlobID>,
        usize,
        &str,
    ),
) {
    let (children, expected_children, filtered, regex) = input;
    let fm = FolderManifest {
        author: DeviceID::default(),
        timestamp,
        id: VlobID::default(),
        parent: VlobID::default(),
        version: 0,
        created: timestamp,
        updated: timestamp,
        children,
    };

    let lfm =
        LocalFolderManifest::from_remote(fm.clone(), Some(&Regex::from_regex_str(regex).unwrap()));

    p_assert_eq!(lfm.base, fm);
    assert!(!lfm.need_sync);
    p_assert_eq!(lfm.updated, timestamp);
    p_assert_eq!(lfm.children, expected_children);
    p_assert_eq!(lfm.local_confinement_points.len(), 0);
    p_assert_eq!(lfm.remote_confinement_points.len(), filtered);
    assert!(!lfm.speculative);
}

#[rstest]
#[case::empty(HashMap::new(), HashMap::new(), HashMap::new(), 0, 0, false, "")]
#[case::children_filtered(
    HashMap::from([
        ("file1.png".parse().unwrap(), VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap())
    ]),
    HashMap::new(),
    HashMap::new(),
    1,
    0,
    false,
    ".+",
)]
#[case::children(
    HashMap::from([
        ("file1.png".parse().unwrap(), VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap())
    ]),
    HashMap::new(),
    HashMap::from([
        ("file1.png".parse().unwrap(), VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap())
    ]),
    0,
    0,
    false,
    ".mp4",
)]
#[case::children_merged(
    HashMap::from([
        ("file1.png".parse().unwrap(), VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap())
    ]),
    HashMap::from([
        ("file2.mp4".parse().unwrap(), VlobID::from_hex("3DF3AC53967C43D889860AE2F459F42B").unwrap())
    ]),
    HashMap::from([
        ("file1.png".parse().unwrap(), VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap()),
        ("file2.mp4".parse().unwrap(), VlobID::from_hex("3DF3AC53967C43D889860AE2F459F42B").unwrap()),
    ]),
    0,
    1,
    false,
    ".mp4",
)]
#[case::need_sync(
    HashMap::new(),
    HashMap::from([
        ("file2.mp4".parse().unwrap(), VlobID::from_hex("3DF3AC53967C43D889860AE2F459F42B").unwrap())
    ]),
    HashMap::from([
        ("file2.mp4".parse().unwrap(), VlobID::from_hex("3DF3AC53967C43D889860AE2F459F42B").unwrap()),
    ]),
    0,
    0,
    true,
    ".png",
)]
fn local_folder_manifest_from_remote_with_local_context(
    timestamp: DateTime,
    #[case] children: HashMap<EntryName, VlobID>,
    #[case] local_children: HashMap<EntryName, VlobID>,
    #[case] expected_children: HashMap<EntryName, VlobID>,
    #[case] filtered: usize,
    #[case] merged: usize,
    #[case] need_sync: bool,
    #[case] regex: &str,
) {
    let fm = FolderManifest {
        author: DeviceID::default(),
        timestamp,
        id: VlobID::default(),
        parent: VlobID::default(),
        version: 0,
        created: timestamp,
        updated: timestamp,
        children,
    };

    let lfm = LocalFolderManifest {
        base: fm.clone(),
        need_sync: false,
        updated: timestamp,
        children: local_children.clone(),
        local_confinement_points: local_children.into_values().collect(),
        remote_confinement_points: HashSet::new(),
        speculative: false,
    };

    let lfm = LocalFolderManifest::from_remote_with_local_context(
        fm.clone(),
        Some(&Regex::from_regex_str(regex).unwrap()),
        &lfm,
        timestamp,
    );

    p_assert_eq!(lfm.base, fm);
    p_assert_eq!(lfm.need_sync, need_sync);
    p_assert_eq!(lfm.updated, timestamp);
    p_assert_eq!(lfm.children, expected_children);
    p_assert_eq!(lfm.local_confinement_points.len(), merged);
    p_assert_eq!(lfm.remote_confinement_points.len(), filtered);
    assert!(!lfm.speculative);
}

#[rstest]
fn local_folder_manifest_to_remote(timestamp: DateTime) {
    let t1 = timestamp;
    let t2 = t1.add_us(1);
    let author = DeviceID::default();
    let parent = VlobID::default();
    let mut lfm = LocalFolderManifest::new(author, parent, t1);

    lfm.children
        .insert("file1.png".parse().unwrap(), VlobID::default());
    lfm.updated = t2;

    let author = DeviceID::default();
    let fm = lfm.to_remote(author.clone(), timestamp);

    p_assert_eq!(fm.author, author);
    p_assert_eq!(fm.timestamp, timestamp);
    p_assert_eq!(fm.id, lfm.base.id);
    p_assert_eq!(fm.parent, lfm.base.parent);
    p_assert_eq!(fm.version, lfm.base.version + 1);
    p_assert_eq!(fm.created, lfm.base.created);
    p_assert_eq!(fm.updated, lfm.updated);
    p_assert_eq!(fm.children, lfm.children);
}

#[rstest]
fn local_folder_manifest_match_remote(timestamp: DateTime) {
    let fm = FolderManifest {
        author: DeviceID::default(),
        timestamp,
        id: VlobID::default(),
        parent: VlobID::default(),
        version: 0,
        created: timestamp,
        updated: timestamp,
        children: HashMap::new(),
    };

    let lfm = LocalFolderManifest {
        base: fm.clone(),
        need_sync: false,
        updated: timestamp,
        children: HashMap::new(),
        local_confinement_points: HashSet::new(),
        remote_confinement_points: HashSet::new(),
        speculative: false,
    };

    assert!(lfm.match_remote(&fm));
}

#[rstest]
#[case::empty(HashMap::new(), HashMap::new(), HashMap::new(), 0, false, "")]
#[case::no_data(
    HashMap::new(),
    HashMap::from([
        ("file2.mp4".parse().unwrap(), VlobID::from_hex("3DF3AC53967C43D889860AE2F459F42B").unwrap())
    ]),
    HashMap::from([
        ("file2.mp4".parse().unwrap(), VlobID::from_hex("3DF3AC53967C43D889860AE2F459F42B").unwrap())
    ]),
    0,
    false,
    ".mp4",
)]
#[case::data(
    HashMap::from([
        ("file1.png".parse().unwrap(), Some(VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap())),
        ("file2.mp4".parse().unwrap(), Some(VlobID::from_hex("3DF3AC53967C43D889860AE2F459F42B").unwrap())),
    ]),
    HashMap::from([
        ("file2.mp4".parse().unwrap(), VlobID::from_hex("3DF3AC53967C43D889860AE2F459F42B").unwrap())
    ]),
    HashMap::from([
        ("file1.png".parse().unwrap(), VlobID::from_hex("936DA01F9ABD4d9d80C702AF85C822A8").unwrap()),
        ("file2.mp4".parse().unwrap(), VlobID::from_hex("3DF3AC53967C43D889860AE2F459F42B").unwrap()),
    ]),
    1,
    true,
    ".png",
)]
fn local_folder_manifest_evolve_children_and_mark_updated(
    timestamp: DateTime,
    #[case] data: HashMap<EntryName, Option<VlobID>>,
    #[case] children: HashMap<EntryName, VlobID>,
    #[case] expected_children: HashMap<EntryName, VlobID>,
    #[case] merged: usize,
    #[case] need_sync: bool,
    #[case] regex: &str,
) {
    let prevent_sync_pattern = Regex::from_regex_str(regex).unwrap();

    let fm = FolderManifest {
        author: DeviceID::default(),
        timestamp,
        id: VlobID::default(),
        parent: VlobID::default(),
        version: 0,
        created: timestamp,
        updated: timestamp,
        children: HashMap::new(),
    };

    let lfm = LocalFolderManifest {
        base: fm.clone(),
        need_sync: false,
        updated: timestamp,
        children,
        local_confinement_points: HashSet::new(),
        remote_confinement_points: HashSet::new(),
        speculative: false,
    }
    .evolve_children_and_mark_updated(data, Some(&prevent_sync_pattern), timestamp);

    p_assert_eq!(lfm.base, fm);
    p_assert_eq!(lfm.need_sync, need_sync);
    p_assert_eq!(lfm.updated, timestamp);
    p_assert_eq!(lfm.children, expected_children);
    p_assert_eq!(lfm.local_confinement_points.len(), merged);
    p_assert_eq!(lfm.remote_confinement_points.len(), 0);
}

// TODO
#[rstest]
fn local_folder_manifest_apply_prevent_sync_pattern(timestamp: DateTime) {
    let prevent_sync_pattern = Regex::from_regex_str("").unwrap();

    let fm = FolderManifest {
        author: DeviceID::default(),
        timestamp,
        id: VlobID::default(),
        parent: VlobID::default(),
        version: 0,
        created: timestamp,
        updated: timestamp,
        children: HashMap::new(),
    };

    let lfm = LocalFolderManifest {
        base: fm.clone(),
        need_sync: false,
        updated: timestamp,
        children: HashMap::new(),
        local_confinement_points: HashSet::new(),
        remote_confinement_points: HashSet::new(),
        speculative: false,
    }
    .apply_prevent_sync_pattern(Some(&prevent_sync_pattern), timestamp);

    p_assert_eq!(lfm.base, fm);
    assert!(!lfm.need_sync);
    p_assert_eq!(lfm.updated, timestamp);
    p_assert_eq!(lfm.children, HashMap::new());
    p_assert_eq!(lfm.local_confinement_points, HashSet::new());
    p_assert_eq!(lfm.remote_confinement_points, HashSet::new());
}

#[rstest]
fn local_user_manifest_new(timestamp: DateTime) {
    let author = DeviceID::default();
    let id = VlobID::default();
    let speculative = false;
    let lum = LocalUserManifest::new(author.clone(), timestamp, Some(id), speculative);

    p_assert_eq!(lum.base.id, id);
    p_assert_eq!(lum.base.author, author);
    p_assert_eq!(lum.base.timestamp, timestamp);
    p_assert_eq!(lum.base.version, 0);
    p_assert_eq!(lum.base.created, timestamp);
    p_assert_eq!(lum.base.updated, timestamp);
    assert!(lum.need_sync);
    p_assert_eq!(lum.updated, timestamp);
    p_assert_eq!(lum.local_workspaces.len(), 0);
    p_assert_eq!(lum.speculative, speculative);
}

#[rstest]
fn local_user_manifest_from_remote(
    #[values(false, true)] with_workspaces_legacy_initial_info: bool,
    timestamp: DateTime,
) {
    let workspaces_legacy_initial_info = {
        let mut workspaces_legacy_initial_info = vec![];
        if with_workspaces_legacy_initial_info {
            workspaces_legacy_initial_info.push(LegacyUserManifestWorkspaceEntry {
                name: "wksp1".parse().unwrap(),
                id: VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                key: SecretKey::from(hex!(
                    "6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57"
                )),
                encryption_revision: 1,
            })
        }
        workspaces_legacy_initial_info
    };

    let um = UserManifest {
        author: DeviceID::default(),
        timestamp,
        id: VlobID::default(),
        version: 0,
        created: timestamp,
        updated: timestamp,
        workspaces_legacy_initial_info,
    };

    let lum = LocalUserManifest::from_remote(um.clone());

    p_assert_eq!(lum.base, um);
    assert!(!lum.need_sync);
    p_assert_eq!(lum.updated, timestamp);
    p_assert_eq!(lum.local_workspaces, vec![]);
}

#[rstest]
fn local_user_manifest_to_remote(
    #[values(false, true)] with_workspaces_legacy_initial_info: bool,
    timestamp: DateTime,
) {
    let t1 = timestamp;
    let t2 = t1.add_us(1);
    let author = DeviceID::default();
    let id = VlobID::default();
    let speculative = false;
    let lum = {
        let mut lum = LocalUserManifest::new(author, t1, Some(id), speculative);
        lum.local_workspaces.push(LocalUserManifestWorkspaceEntry {
            id: VlobID::default(),
            name: "wksp1".parse().unwrap(),
            name_origin: CertificateBasedInfoOrigin::Placeholder,
            role: RealmRole::Contributor,
            role_origin: CertificateBasedInfoOrigin::Placeholder,
        });
        lum.updated = t2;
        if with_workspaces_legacy_initial_info {
            lum.base
                .workspaces_legacy_initial_info
                .push(LegacyUserManifestWorkspaceEntry {
                    name: "wksp1".parse().unwrap(),
                    id: VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    key: SecretKey::from(hex!(
                        "6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57"
                    )),
                    encryption_revision: 1,
                });
        }
        lum
    };

    let author = DeviceID::default();
    let um = lum.to_remote(author.clone(), timestamp);

    p_assert_eq!(um.author, author);
    p_assert_eq!(um.timestamp, timestamp);
    p_assert_eq!(um.id, lum.base.id);
    p_assert_eq!(um.version, lum.base.version + 1);
    p_assert_eq!(um.created, lum.base.created);
    p_assert_eq!(um.updated, lum.updated);
    p_assert_eq!(
        um.workspaces_legacy_initial_info,
        lum.base.workspaces_legacy_initial_info
    );
}

#[rstest]
fn local_user_manifest_match_remote(
    #[values(false, true)] with_workspaces_legacy_initial_info: bool,
    timestamp: DateTime,
) {
    let um = {
        let mut um = UserManifest {
            author: DeviceID::default(),
            timestamp,
            id: VlobID::default(),
            version: 0,
            created: timestamp,
            updated: timestamp,
            workspaces_legacy_initial_info: vec![],
        };
        if with_workspaces_legacy_initial_info {
            um.workspaces_legacy_initial_info
                .push(LegacyUserManifestWorkspaceEntry {
                    name: "wksp1".parse().unwrap(),
                    id: VlobID::from_hex("b82954f1138b4d719b7f5bd78915d20f").unwrap(),
                    key: SecretKey::from(hex!(
                        "6507907d33bae6b5980b32fa03f3ebac56141b126e44f352ea46c5f22cd5ac57"
                    )),
                    encryption_revision: 1,
                });
        }
        um
    };

    let lum = LocalUserManifest {
        base: um.clone(),
        need_sync: false,
        updated: timestamp,
        local_workspaces: vec![],
        speculative: false,
    };

    assert!(lum.match_remote(&um));
}
