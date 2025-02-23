# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 (eventually AGPL-3.0) 2016-present Scille SAS

# flake8: noqa

import trio
import tempfile
from protocol.utils import *

from parsec._parsec import save_recovery_device, save_device_with_password, SecretKey
from parsec.api.protocol import *
from parsec.api.data import *
from parsec.core.types import *
from parsec.core.local_device import *


with tempfile.NamedTemporaryFile(suffix=".psrk") as fp:
    passphrase = trio.run(save_recovery_device, Path(fp.name), ALICE, True)
    fp.seek(0)
    raw = fp.read()
content = display(f"recovery device file (passphrase: {passphrase})", raw, [])
key = SecretKey.from_recovery_passphrase(passphrase=passphrase)
display(f"recovery device file content", content["ciphertext"], [key])

with tempfile.NamedTemporaryFile(suffix=".keys") as fp:
    password = "P@ssw0rd."
    save_device_with_password(Path(fp.name), ALICE, password, True)
    fp.seek(0)
    raw = fp.read()
content = display(f"device file (password: {password})", raw, [])
key = SecretKey.from_password(password, salt=content["salt"])

raw = DeviceFile(
    type=DeviceFileType.SMARTCARD,
    ciphertext=content["ciphertext"],
    human_handle=ALICE.human_handle,
    device_label=ALICE.device_label,
    device_id=ALICE.device_id,
    organization_id=ALICE.organization_id,
    slug=ALICE.slug,
    salt=None,
    encrypted_key=b"foo",
    certificate_id="foo",
    certificate_sha1=b"foo",
).dump()

display("device smartcard", raw, [])
