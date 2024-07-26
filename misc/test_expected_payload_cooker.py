# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS
r"""
This script helps to fix old/legacy payloads in libparsec serialization tests.

Serialization tests are usually written in the following structure:
- a hard-coded raw value (the payload)
- a hard-coded expected value corresponding to the payload
- an assert comparing the value loaded from raw to the expected value

Any change impacting the serialization format or the expected value will make
the payload obsolete. This scripts helps regenerate it for the failing test.

1. Add a println with following syntax "***expected: <dumped expected value>"

Example:
```rust
    let raw = hex!(
        //...
    );
    let expected =
        // ...
    ;
    println!("***expected: {:?}", expected.dump());
    // ...
    p_assert_eq!(data, expected);

2. Run the failing test(s) and check that the print is displayed

3. Run the failing test(s) redirecting stderr to stdout and pipe its output
   int this script

Example:
```shell
$ cargo nextest run -p libparsec_protocol 2>&1 | python ./misc/test_expected_payload_cooker.py

================== libparsec_protocol::serialization anonymous_cmds::v4::organization_bootstrap_rep_timestamp_out_of_ballpark ==================

    // Generated from Parsec v3.0.0-b.11+dev
    "85a6737461747573b974696d657374616d705f6f75745f6f665f62616c6c7061726bbc"
    "62616c6c7061726b5f636c69656e745f6561726c795f6f6666736574cb4072c0000000"
    "0000bb62616c6c7061726b5f636c69656e745f6c6174655f6f6666736574cb40740000"
    "00000000b0636c69656e745f74696d657374616d70d70100035d162fa2e400b0736572"
    "7665725f74696d657374616d70d70100035d162fa2e400"
```

So for each failing tests, the script will print:
- the name of the test
- a comment line with the libparsec version used to generate the payload
- a comment line with the content of the payload (if possible, see TODO comment below)
- the corresponding raw value (aka payload)

You should then:
1. Replace the test's payload with the one printed by this script.
2. Replace the test's comment line containing the libparsec version
3. Replace the test's comment line containing the expected value (if printed by this script)
4. Remove the println
5. Re-run test(s) which should not fail anymore \o/
"""

import binascii
import datetime
import io
import os
import re
import struct
import sys
import textwrap

try:
    import msgpack  # type: ignore
except ImportError:
    raise SystemExit("msgpack not installed. Run `pip install msgpack`")
try:
    import zstandard  # type: ignore
except ImportError:
    raise SystemExit("zstandard not installed. Run `pip install zstandard`")
try:
    import nacl.exceptions  # type: ignore
    import nacl.secret  # type: ignore
except ImportError:
    raise SystemExit("pynacl not installed. Run `pip install pynacl`")

# File containing the current version of libparsec
LIBPARSEC_VERSION_FILE = os.path.join(os.path.dirname(__file__), "..", "libparsec", "version")

# Expected failure header: `FAIL [   0.004s] libparsec_types certif::tests::serde_user_certificate_redacted`
FAILING_TEST_HEADER_PATTERN = re.compile(r"\W*FAIL \[[ 0-9.]+s\] ([ \w::]+)")

# Expected print message: `***expected: <dump>`
##     println!("***expected: {:?}", expected.dump());
TAG_PATTERN = re.compile(r"\W*\*\*\*expected: \[([ 0-9,]*)\]")

KEY_CANDIDATES = [
    binascii.unhexlify("b1b52e16c1b46ab133c8bf576e82d26c887f1e9deae1af80043a258c36fcabf3")
]


def decode_expected_raw(raw: bytes) -> dict[str, object]:
    def attempt_decrypt(raw: bytes) -> bytes | None:
        for key in KEY_CANDIDATES:
            key = nacl.secret.SecretBox(key)
            try:
                return key.decrypt(raw)
            except nacl.exceptions.CryptoError:
                continue

    def attempt_deserialization(raw: bytes) -> dict[str, object] | None:
        if raw[0] == 0xFF:
            try:
                return msgpack.unpackb(raw[1:])
            except ValueError:
                pass

        # First byte is the version
        if raw[0] != 0x00:
            return None

        try:
            io_input = io.BytesIO(raw[1:])
            io_output = io.BytesIO()
            decompressor = zstandard.ZstdDecompressor()
            decompressor.copy_stream(io_input, io_output)
            decompressed = io_output.getvalue()
        except zstandard.ZstdError:
            return None

        try:
            # `strict_map_key` is needed because shamir_recovery_brief_certificate
            # uses `DeviceID` (i.e. ExtType) as dict key.
            return msgpack.unpackb(decompressed, strict_map_key=False)
        except ValueError:
            return None

    # First attempt: consider the data is not signed nor encrypted
    deserialized = attempt_deserialization(raw)
    if deserialized is not None:
        return deserialized

    # Second attempt: consider the data is only signed
    raw_without_signature = raw[64:]
    deserialized = attempt_deserialization(raw_without_signature)
    if deserialized is not None:
        return deserialized

    # Last attempt: consider the data is encrypted...
    decrypted = attempt_decrypt(raw)
    assert decrypted is not None
    # ...and signed ?
    decrypted_without_signature = decrypted[64:]
    deserialized = attempt_deserialization(decrypted_without_signature)
    if deserialized is None:
        # ...or not signed ?
        deserialized = attempt_deserialization(decrypted)
    assert deserialized is not None
    return deserialized


def cook_msgpack_type(value):
    if isinstance(value, bytes):
        return f"0x{value.hex()}"

    if isinstance(value, msgpack.ExtType):
        match value.code:
            # DateTime
            case 1:
                ts = struct.unpack(">q", value.data)[0]
                dt = datetime.datetime.fromtimestamp(ts / 1000000).isoformat() + "Z"
                return f"ext(1, {ts}) i.e. {dt}"
            # UUID
            case 2:
                return f"ext(2, 0x{value.data.hex()})"

            case _:
                pass

    if isinstance(value, dict):
        out = "{ "
        for k, v in value.items():
            if not isinstance(k, str):
                k = cook_msgpack_type(k)
            out += f"{k}: {cook_msgpack_type(v)}, "
        out += "}"
        return out

    if isinstance(value, list):
        out = "[ "
        for v in value:
            out += f"{cook_msgpack_type(v)}, "
        out += "]"
        return out

    return repr(value)


def parse_lines(lines):
    current_test = None

    for line in lines:
        match_failing_test = FAILING_TEST_HEADER_PATTERN.match(line)
        if match_failing_test:
            current_test = match_failing_test.group(1)

        match_print_expected = TAG_PATTERN.match(line)
        if not match_print_expected:
            continue

        expected_raw = bytes(
            bytearray([int(byte.strip()) for byte in match_print_expected.group(1).split(",")])
        )

        expected_decoded = decode_expected_raw(expected_raw)

        output_lines = []

        with open(LIBPARSEC_VERSION_FILE) as f:
            libparsec_version = f.readline()

        output_lines.append(f"    // Generated from Parsec {libparsec_version}")

        output_lines.append("    // Content:")
        for k, v in expected_decoded.items():
            output_lines.append(f"    //   {k}: {cook_msgpack_type(v)}")

        output_lines.append("    let data = &hex!(")

        # The raw value (payload) to be used in the test
        for part in textwrap.wrap(expected_raw.hex()):
            output_lines.append(f'    "{part}"')

        output_lines.append("    );")

        print()
        print(f"================== {current_test} ==================")
        print()
        print("\n".join(output_lines))


if __name__ == "__main__":
    parse_lines(sys.stdin.readlines())
