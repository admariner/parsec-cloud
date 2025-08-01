-- Parsec Cloud (https://parsec.cloud) Copyright (c) BUSL-1.1 2016-present Scille SAS

-- This SQL script is not actually used to initialize the database: we rely
-- on all the migrations scripts for that (even if the database is brand new !).
-- The true role of this script is to provide a unified and up to date view
-- of the current datamodel.
-- On top of that we test the migrations and this script against each other to
-- ensure consistency.

-------------------------------------------------------
--  Account
-------------------------------------------------------


CREATE TABLE account (
    _id SERIAL PRIMARY KEY,
    email VARCHAR(254) UNIQUE NOT NULL,
    -- Not used by Parsec Account but works as a quality-of-life feature
    -- to allow pre-filling human handle during enrollment.
    human_handle_label VARCHAR(254) NOT NULL,
    -- Account marked as deleted is a special case:
    -- - By definition, a deleted account shouldn't be present in the database...
    -- - ...however it is convenient to leave the actual deletion to a dedicated script run
    --   periodically (this typically simplifies the recovery of an account deleted by mistake).
    -- In a nutshell: an account marked as deleted is always ignored, except when creating
    -- a new account in which case the deleted account is not overwritten but instead restored
    -- (i.e. `deleted_on` is set to NULL, and a new vault & authentication method is inserted).
    --
    -- NULL if not deleted
    deleted_on TIMESTAMPTZ
);


CREATE TABLE vault (
    _id SERIAL PRIMARY KEY,
    account INTEGER REFERENCES account (_id) NOT NULL
);


CREATE TABLE vault_item (
    _id SERIAL PRIMARY KEY,
    vault INTEGER REFERENCES vault (_id) NOT NULL,
    fingerprint BYTEA NOT NULL,
    data BYTEA NOT NULL,
    UNIQUE (vault, fingerprint)
);


CREATE TYPE password_algorithm AS ENUM ('ARGON2ID');


CREATE TABLE vault_authentication_method (
    _id SERIAL PRIMARY KEY,
    auth_method_id UUID UNIQUE NOT NULL,
    vault INTEGER REFERENCES vault (_id) NOT NULL,
    created_on TIMESTAMPTZ NOT NULL,
    -- IP address of the HTTP request that created the authentication method
    -- (either by account creation, vault key rotation or account recovery)
    -- Can be unknown (i.e. empty string) since this information is optional in
    -- ASGI (see
    -- https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope).
    created_by_ip TEXT NOT NULL,
    -- User agent header of the HTTP request that created the vault.
    created_by_user_agent TEXT NOT NULL,
    -- Secret key used for HMAC based authentication with the server
    mac_key BYTEA NOT NULL,
    -- Vault key encrypted with the `auth_method_secret_key` see rfc 1014
    vault_key_access BYTEA NOT NULL,
    -- Auth method can be of two types:
    -- - ClientProvided, for which the client is able to store
    --   `auth_method_master_secret` all by itself.
    -- - Password, for which the client must obtain some configuration
    --   (i.e. this field !) from the server in order to know how
    --   to turn the password into `auth_method_master_secret`.
    -- NULL in case of `ClientProvided`.
    password_algorithm PASSWORD_ALGORITHM,
    -- `password_algorithm_argon2id_*` fields are expected to be:
    -- - NOT NULL if `password_algorithm` == 'ARGON2ID'
    -- - NULL if `password_algorithm` != 'ARGON2ID'
    password_algorithm_argon2id_opslimit INTEGER,
    password_algorithm_argon2id_memlimit_kb INTEGER,
    password_algorithm_argon2id_parallelism INTEGER,
    -- Note that only the current vault contains auth methods that are not disabled
    -- NULL if not disabled
    disabled_on TIMESTAMPTZ
);


CREATE TABLE account_create_validation_code (
    email VARCHAR(256) PRIMARY KEY NOT NULL,
    validation_code VARCHAR(6) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    failed_attempts INTEGER DEFAULT 0
);


CREATE TABLE account_delete_validation_code (
    account INTEGER REFERENCES account (_id) NOT NULL PRIMARY KEY,
    validation_code VARCHAR(6) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    failed_attempts INTEGER DEFAULT 0
);


CREATE TABLE account_recover_validation_code (
    account INTEGER REFERENCES account (_id) NOT NULL PRIMARY KEY,
    validation_code VARCHAR(6) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    failed_attempts INTEGER DEFAULT 0
);

-------------------------------------------------------
--  Organization
-------------------------------------------------------


CREATE TYPE allowed_client_agent AS ENUM ('NATIVE_ONLY', 'NATIVE_OR_WEB');
CREATE TYPE account_vault_strategy AS ENUM ('ALLOWED', 'FORBIDDEN');

CREATE TABLE organization (
    _id SERIAL PRIMARY KEY,
    organization_id VARCHAR(32) UNIQUE NOT NULL,
    -- NULL if the organization was spontaneously created (i.e. as part
    -- of organization bootstrap)
    bootstrap_token VARCHAR(32),
    -- NULL if not bootstrapped
    root_verify_key BYTEA,
    -- NULL if not expired
    _expired_on TIMESTAMPTZ,
    user_profile_outsider_allowed BOOLEAN NOT NULL,
    -- NULL if no limit
    active_users_limit INTEGER,
    is_expired BOOLEAN NOT NULL,
    -- NULL if not bootstrapped
    _bootstrapped_on TIMESTAMPTZ,
    _created_on TIMESTAMPTZ NOT NULL,
    -- NULL for non-sequestered organization
    sequester_authority_certificate BYTEA,
    -- NULL for non-sequestered organization
    sequester_authority_verify_key_der BYTEA,
    minimum_archiving_period INTEGER NOT NULL,
    -- NULL if no Term Of Service (TOS) is set
    tos_updated_on TIMESTAMPTZ,
    -- NULL if no Term Of Service (TOS) is set
    -- Stores as JSON a mapping of locale as key and URL as value
    -- e.g. {"en_US": "https://example.com/tos_en.html", "fr_FR": "https://example.com/tos_fr.html"}
    tos_per_locale_urls JSON,
    allowed_client_agent ALLOWED_CLIENT_AGENT NOT NULL,
    account_vault_strategy ACCOUNT_VAULT_STRATEGY NOT NULL
);

-------------------------------------------------------
-- Sequester
-------------------------------------------------------
CREATE TYPE sequester_service_type AS ENUM ('STORAGE', 'WEBHOOK');

CREATE TABLE sequester_service (
    _id SERIAL PRIMARY KEY,
    service_id UUID NOT NULL,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    service_certificate BYTEA NOT NULL,
    service_label VARCHAR(254) NOT NULL,
    created_on TIMESTAMPTZ NOT NULL,
    disabled_on TIMESTAMPTZ, -- NULL if currently enabled
    webhook_url TEXT, -- NULL if service_type != WEBHOOK;
    service_type SEQUESTER_SERVICE_TYPE NOT NULL,

    revoked_on TIMESTAMPTZ, -- NULL if not yet revoked
    sequester_revoked_service_certificate BYTEA, -- NULL if not yet revoked

    UNIQUE (organization, service_id)
);

-------------------------------------------------------
--  User
-------------------------------------------------------


CREATE TABLE human (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    email VARCHAR(254) NOT NULL,
    label VARCHAR(254) NOT NULL,

    UNIQUE (organization, email)
);


CREATE TYPE user_profile AS ENUM ('ADMIN', 'STANDARD', 'OUTSIDER');


CREATE TABLE user_ (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    user_id UUID NOT NULL,
    user_certificate BYTEA NOT NULL,
    -- NULL if certifier is the Root Verify Key
    user_certifier INTEGER,
    created_on TIMESTAMPTZ NOT NULL,
    -- NULL if not yet revoked
    revoked_on TIMESTAMPTZ,
    -- NULL if not yet revoked
    revoked_user_certificate BYTEA,
    -- NULL if not yet revoked
    revoked_user_certifier INTEGER,
    human INTEGER REFERENCES human (_id) NOT NULL,
    redacted_user_certificate BYTEA NOT NULL,
    initial_profile USER_PROFILE NOT NULL,
    -- This field is altered in an `ALTER TABLE` statement below
    -- in order to avoid cross-reference issues
    shamir_recovery INTEGER,
    -- `frozen` is just a service-side access control flag to indicate the
    -- user should not be allowed to authenticate anymore.
    -- From a data consistency point of view, it is okay to let a frozen user
    -- do anything it should normally be allowed to do.
    -- For this reason, this check is expected to be enforced loosely during
    -- authentication (so outside of the current operation actual transaction).
    frozen BOOLEAN NOT NULL DEFAULT FALSE,
    current_profile USER_PROFILE NOT NULL,
    -- NULL if no End User License Agreement has been accepted
    tos_accepted_on TIMESTAMPTZ,

    UNIQUE (organization, user_id)
);

CREATE TABLE profile (
    _id SERIAL PRIMARY KEY,
    user_ INTEGER REFERENCES user_ (_id) NOT NULL,
    profile USER_PROFILE NOT NULL,
    profile_certificate BYTEA NOT NULL,
    certified_by INTEGER NOT NULL,
    certified_on TIMESTAMPTZ NOT NULL
);


CREATE TABLE device (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    user_ INTEGER REFERENCES user_ (_id) NOT NULL,
    device_id UUID NOT NULL,
    device_label VARCHAR(254) NOT NULL,
    verify_key BYTEA NOT NULL,
    device_certificate BYTEA NOT NULL,
    -- NULL if certifier is the Root Verify Key
    device_certifier INTEGER REFERENCES device (_id),
    created_on TIMESTAMPTZ NOT NULL,
    redacted_device_certificate BYTEA NOT NULL,

    UNIQUE (organization, device_id)
);


ALTER TABLE user_
ADD CONSTRAINT fk_user_device_user_certifier FOREIGN KEY (
    user_certifier
) REFERENCES device (_id);
ALTER TABLE user_
ADD CONSTRAINT fk_user_device_revoked_user_certifier FOREIGN KEY (
    revoked_user_certifier
) REFERENCES device (_id);

ALTER TABLE profile ADD FOREIGN KEY (certified_by) REFERENCES device (_id);

-------------------------------------------------------
--  Shamir recovery
-------------------------------------------------------


CREATE TABLE shamir_recovery_setup (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    user_ INTEGER REFERENCES user_ (_id) NOT NULL,

    brief_certificate BYTEA NOT NULL,
    reveal_token VARCHAR(32) NOT NULL,
    threshold INTEGER NOT NULL,
    shares INTEGER NOT NULL,
    ciphered_data BYTEA,

    -- Added in migration 0007
    created_on TIMESTAMPTZ NOT NULL,
    deleted_on TIMESTAMPTZ,
    deletion_certificate BYTEA,

    UNIQUE (organization, reveal_token)
);


-- Makes sure that there is only one active setup per user
CREATE UNIQUE INDEX unique_active_setup ON shamir_recovery_setup (user_)
WHERE deleted_on IS NULL;


CREATE TABLE shamir_recovery_share (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,

    shamir_recovery INTEGER REFERENCES shamir_recovery_setup (_id) NOT NULL,
    recipient INTEGER REFERENCES user_ (_id) NOT NULL,

    share_certificate BYTEA NOT NULL,
    shares INTEGER NOT NULL,

    UNIQUE (organization, shamir_recovery, recipient)
);


-- Alter user table to introduce a cross-reference between user id and shamir id
ALTER TABLE user_ ADD FOREIGN KEY (
    shamir_recovery
) REFERENCES shamir_recovery_setup (_id);


-------------------------------------------------------
--  Invitation
-------------------------------------------------------

CREATE TYPE invitation_type AS ENUM ('USER', 'DEVICE', 'SHAMIR_RECOVERY');
CREATE TYPE invitation_deleted_reason AS ENUM (
    'FINISHED', 'CANCELLED', 'ROTTEN'
);

CREATE TYPE cancelled_greeting_attempt_reason AS ENUM (
    'MANUALLY_CANCELLED',
    'INVALID_NONCE_HASH',
    'INVALID_SAS_CODE',
    'UNDECIPHERABLE_PAYLOAD',
    'UNDESERIALIZABLE_PAYLOAD',
    'INCONSISTENT_PAYLOAD',
    'AUTOMATICALLY_CANCELLED'
);

CREATE TYPE greeter_or_claimer AS ENUM (
    'GREETER',
    'CLAIMER'
);


CREATE TABLE invitation (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    token VARCHAR(32) NOT NULL,
    type INVITATION_TYPE NOT NULL,

    -- A more readable ordering of these columns would be:
    --
    --     -- Invitation created by either a device or a service
    --     created_by_device INTEGER REFERENCES device (_id),
    --     created_by_service_label VARCHAR(254),
    --
    --     -- Type specific fields
    --     -- Required when type=USER
    --     user_invitation_claimer_email VARCHAR(255),
    --     -- Required when type=DEVICE
    --     device_invitation_claimer INTEGER REFERENCES user_ (_id),
    --     -- Required when type=SHAMIR_RECOVERY
    --     shamir_recovery INTEGER REFERENCES shamir_recovery_setup (_id),
    --
    --     -- Other fields
    --     created_on TIMESTAMPTZ NOT NULL,
    --     deleted_on TIMESTAMPTZ,
    --     deleted_reason INVITATION_DELETED_REASON,

    -- Updated in migration 0009
    created_by_device INTEGER REFERENCES device (_id),

    -- Required when type=USER
    user_invitation_claimer_email VARCHAR(255),

    created_on TIMESTAMPTZ NOT NULL,
    deleted_on TIMESTAMPTZ,
    deleted_reason INVITATION_DELETED_REASON,

    -- Required when type=SHAMIR_RECOVERY
    shamir_recovery INTEGER REFERENCES shamir_recovery_setup (_id),

    -- Added in migration 0009
    created_by_service_label VARCHAR(254),
    -- Required when type=DEVICE
    device_invitation_claimer INTEGER REFERENCES user_ (_id),

    UNIQUE (organization, token)
);

CREATE TABLE greeting_session (
    _id SERIAL PRIMARY KEY,
    invitation INTEGER REFERENCES invitation (_id) NOT NULL,
    greeter INTEGER REFERENCES user_ (_id) NOT NULL,

    UNIQUE (invitation, greeter)
);

CREATE TABLE greeting_attempt (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    greeting_attempt_id UUID NOT NULL,
    greeting_session INTEGER REFERENCES greeting_session (_id) NOT NULL,

    claimer_joined TIMESTAMPTZ DEFAULT NULL,
    greeter_joined TIMESTAMPTZ DEFAULT NULL,

    cancelled_reason CANCELLED_GREETING_ATTEMPT_REASON DEFAULT NULL,
    cancelled_on TIMESTAMPTZ DEFAULT NULL,
    cancelled_by GREETER_OR_CLAIMER DEFAULT NULL,

    UNIQUE (organization, greeting_attempt_id)
);

-- Makes sure that there is only one active greeting attempt per session
CREATE UNIQUE INDEX unique_active_attempt ON greeting_attempt (greeting_session)
WHERE cancelled_on IS NULL;

CREATE TABLE greeting_step (
    _id SERIAL PRIMARY KEY,
    greeting_attempt INTEGER REFERENCES greeting_attempt (_id) NOT NULL,
    step INTEGER NOT NULL,
    greeter_data BYTEA,
    claimer_data BYTEA,

    UNIQUE (greeting_attempt, step)
);

-------------------------------------------------------
--  PKI enrollment
-------------------------------------------------------


CREATE TYPE enrollment_state AS ENUM (
    'SUBMITTED',
    'ACCEPTED',
    'REJECTED',
    'CANCELLED'
);

CREATE TYPE pki_enrollment_info_accepted AS (
    accepted_on TIMESTAMPTZ,
    accepter_der_x509_certificate BYTEA,
    accept_payload_signature BYTEA,
    accept_payload BYTEA
);

CREATE TYPE pki_enrollment_info_rejected AS (
    rejected_on TIMESTAMPTZ
);

CREATE TYPE pki_enrollment_info_cancelled AS (
    cancelled_on TIMESTAMPTZ
);

CREATE TABLE pki_enrollment (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,

    enrollment_id UUID NOT NULL,
    submitter_der_x509_certificate BYTEA NOT NULL,
    submitter_der_x509_certificate_sha1 BYTEA NOT NULL,

    submit_payload_signature BYTEA NOT NULL,
    submit_payload BYTEA NOT NULL,
    submitted_on TIMESTAMPTZ NOT NULL,

    accepter INTEGER REFERENCES device (_id),
    submitter_accepted_device INTEGER REFERENCES device (_id),

    enrollment_state ENROLLMENT_STATE NOT NULL DEFAULT 'SUBMITTED',
    info_accepted PKI_ENROLLMENT_INFO_ACCEPTED,
    info_rejected PKI_ENROLLMENT_INFO_REJECTED,
    info_cancelled PKI_ENROLLMENT_INFO_CANCELLED,

    UNIQUE (organization, enrollment_id)
);

-------------------------------------------------------
--  Realm
-------------------------------------------------------


CREATE TYPE maintenance_type AS ENUM ('REENCRYPTION', 'GARBAGE_COLLECTION');


CREATE TABLE realm (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    realm_id UUID NOT NULL,
    key_index INTEGER NOT NULL,
    created_on TIMESTAMPTZ NOT NULL,

    UNIQUE (organization, realm_id)
);


CREATE TYPE realm_role AS ENUM ('OWNER', 'MANAGER', 'CONTRIBUTOR', 'READER');


CREATE TABLE realm_user_role (
    _id SERIAL PRIMARY KEY,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    user_ INTEGER REFERENCES user_ (_id) NOT NULL,
    -- NULL if access revocation
    role REALM_ROLE,
    certificate BYTEA NOT NULL,
    certified_by INTEGER REFERENCES device (_id) NOT NULL,
    certified_on TIMESTAMPTZ NOT NULL
);

CREATE TYPE realm_archiving_configuration AS ENUM (
    'AVAILABLE', 'ARCHIVED', 'DELETION_PLANNED'
);

CREATE TABLE realm_archiving (
    _id SERIAL PRIMARY KEY,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    configuration REALM_ARCHIVING_CONFIGURATION NOT NULL,
    -- NULL if not DELETION_PLANNED
    deletion_date TIMESTAMPTZ,
    certificate BYTEA NOT NULL,
    certified_by INTEGER REFERENCES device (_id) NOT NULL,
    certified_on TIMESTAMPTZ NOT NULL
);


-- TODO: Investigate which of those timestamp is really needed
CREATE TABLE realm_user_change (
    _id SERIAL PRIMARY KEY,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    user_ INTEGER REFERENCES user_ (_id) NOT NULL,
    -- The last time this user changed the role of another user
    last_role_change TIMESTAMPTZ,
    -- The last time this user updated a vlob
    last_vlob_update TIMESTAMPTZ,
    -- The last time this user changed the archiving configuration
    last_archiving_change TIMESTAMPTZ,

    UNIQUE (realm, user_)
);


CREATE TABLE realm_keys_bundle (
    _id SERIAL PRIMARY KEY,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    key_index INTEGER NOT NULL,

    realm_key_rotation_certificate BYTEA NOT NULL,
    certified_by INTEGER REFERENCES device (_id) NOT NULL,
    certified_on TIMESTAMPTZ NOT NULL,
    key_canary BYTEA NOT NULL,
    keys_bundle BYTEA NOT NULL,

    UNIQUE (realm, key_index)
);


CREATE TABLE realm_keys_bundle_access (
    _id SERIAL PRIMARY KEY,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    user_ INTEGER REFERENCES user_ (_id) NOT NULL,
    realm_keys_bundle INTEGER REFERENCES realm_keys_bundle (_id) NOT NULL,

    access BYTEA NOT NULL,

    -- Updated in migration 0010
    -- There is two scenarios where a keys bundle access is provided:
    -- - During key rotation, in which each member of the realm got a new access.
    -- - When sharing with a user, in which case only he got a new access.
    --
    -- In practice this means there can be multiple accesses for a given user and
    -- keys bundle pair, but only the most recent is used.
    --
    -- However we still want to keep the others accesses in database (instead of
    -- just overwriting everything but the last one), given:
    -- - It allows simple recovery in case of a bug/malicious client trying to
    --   share with invalid accesses.
    -- - A realm export contains all known accesses so they can all be tried when
    --   decrypting data.
    --
    -- NULL if the keys bundle access comes from a key rotation.
    from_sharing INTEGER REFERENCES realm_user_role (_id)
);


-- TODO: Replace this by a `UNIQUE NULLS NOT DISTINCT` once we upgrade to PostgreSQL 15
CREATE UNIQUE INDEX realm_keys_bundle_access_index_from_sharing_not_null
ON realm_keys_bundle_access (
    realm, user_, realm_keys_bundle, from_sharing
) WHERE from_sharing IS NOT NULL;
CREATE UNIQUE INDEX realm_keys_bundle_access_index_from_sharing_null
ON realm_keys_bundle_access (
    realm, user_, realm_keys_bundle
) WHERE from_sharing IS NULL;


CREATE TABLE realm_sequester_keys_bundle_access (
    _id SERIAL PRIMARY KEY,
    sequester_service INTEGER REFERENCES sequester_service (_id) NOT NULL,
    realm_keys_bundle INTEGER REFERENCES realm_keys_bundle (_id) NOT NULL,

    access BYTEA NOT NULL,

    realm INTEGER REFERENCES realm (_id) NOT NULL,

    UNIQUE (sequester_service, realm_keys_bundle)
);


CREATE TABLE realm_name (
    _id SERIAL PRIMARY KEY,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    realm_name_certificate BYTEA NOT NULL,
    certified_by INTEGER REFERENCES device (_id) NOT NULL,
    certified_on TIMESTAMPTZ NOT NULL
);


-------------------------------------------------------
--  Vlob
-------------------------------------------------------

CREATE TABLE vlob_atom (
    _id SERIAL PRIMARY KEY,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    key_index INTEGER NOT NULL,
    vlob_id UUID NOT NULL,
    version INTEGER NOT NULL,
    blob BYTEA NOT NULL,
    size INTEGER NOT NULL,
    author INTEGER REFERENCES device (_id) NOT NULL,
    created_on TIMESTAMPTZ NOT NULL,
    -- NULL if not deleted
    deleted_on TIMESTAMPTZ,

    UNIQUE (realm, vlob_id, version)
);


CREATE TABLE realm_vlob_update (
    _id SERIAL PRIMARY KEY,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    index INTEGER NOT NULL,
    vlob_atom INTEGER REFERENCES vlob_atom (_id) NOT NULL,

    UNIQUE (realm, index)
);


-------------------------------------------------------
--  Block
-------------------------------------------------------


CREATE TABLE block (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    block_id UUID NOT NULL,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    author INTEGER REFERENCES device (_id) NOT NULL,
    size INTEGER NOT NULL,
    created_on TIMESTAMPTZ NOT NULL,
    -- NULL if not deleted
    deleted_on TIMESTAMPTZ,
    key_index INTEGER NOT NULL,

    UNIQUE (organization, block_id)
);


-- Only used if we store blocks' data in database
CREATE TABLE block_data (
    _id SERIAL PRIMARY KEY,
    -- No reference with organization&block tables given this table
    -- should stay isolated
    organization_id VARCHAR NOT NULL,
    block_id UUID NOT NULL,
    data BYTEA NOT NULL,

    UNIQUE (organization_id, block_id)
);


-------------------------------------------------------
-- Topic
-------------------------------------------------------

CREATE TABLE common_topic (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    last_timestamp TIMESTAMPTZ NOT NULL,
    UNIQUE (organization)

);

CREATE TABLE sequester_topic (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    last_timestamp TIMESTAMPTZ NOT NULL,
    UNIQUE (organization)
);

CREATE TABLE shamir_recovery_topic (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    last_timestamp TIMESTAMPTZ NOT NULL,
    UNIQUE (organization)
);

CREATE TABLE realm_topic (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    realm INTEGER REFERENCES realm (_id) NOT NULL,
    last_timestamp TIMESTAMPTZ NOT NULL,
    UNIQUE (organization, realm)
);


-------------------------------------------------------
--  Migration
-------------------------------------------------------


CREATE TABLE migration (
    _id INTEGER PRIMARY KEY,
    name VARCHAR(256) NOT NULL UNIQUE,
    applied TIMESTAMPTZ NOT NULL
);
