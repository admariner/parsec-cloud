# Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

# Those imports required so that test `server/tests/test_api.py::test_each_cmd_req_rep_has_dedicated_test`
# can successfully discover all API-related tests and decide if some of them are missing.
# ruff: noqa: F403
from .test_account_delete_proceed import *
from .test_account_delete_send_validation_email import *
from .test_account_info import *
from .test_auth_method_create import *
from .test_auth_method_disable import *
from .test_auth_method_list import *
from .test_invite_self_list import *
from .test_organization_self_list import *
from .test_ping import *
from .test_vault_item_list import *
from .test_vault_item_recovery_list import *
from .test_vault_item_upload import *
from .test_vault_key_rotation import *
