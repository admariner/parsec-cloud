// Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

#![allow(clippy::duplicate_mod)]

// The compat module allows to re-use tests from previous major API
#[path = "../v3/invite_3a_claimer_signify_trust.rs"]
mod compat;

use super::invited_cmds;

// Request

pub use compat::req;

// Responses

pub use compat::rep_ok;

pub use compat::rep_already_deleted;

pub use compat::rep_not_found;

pub use compat::rep_invalid_state;