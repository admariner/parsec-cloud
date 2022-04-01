 -- Parsec Cloud (https://parsec.cloud) Copyright (c) BSLv1.1 (eventually AGPLv3) 2016-2021 Scille SAS


-------------------------------------------------------
--  Migration
-------------------------------------------------------

CREATE TYPE enrollment_state AS ENUM (
    'SUBMITTED',
    'ACCEPTED',
    'REJECTED',
    'CANCELLED'
);

CREATE TYPE pki_enrollment_info_accepted AS(
    accepted_on TIMESTAMPTZ,
    accepter_der_x509_certificate BYTEA,
    accept_payload_signature BYTEA,
    accept_payload BYTEA
);

CREATE TYPE pki_enrollment_info_rejected AS(
    rejected_on TIMESTAMPTZ
);

CREATE TYPE pki_enrollment_info_cancelled AS(
    cancelled_on TIMESTAMPTZ
);

CREATE TABLE pki_enrollment (
    _id SERIAL PRIMARY KEY,
    organization INTEGER REFERENCES organization (_id) NOT NULL,
    request_id UUID NOT NULL,
    submitter_der_x509_certificate BYTEA NOT NULL,
    submit_payload_signature BYTEA NOT NULL,
    submit_payload BYTEA NOT NULL,
    submitted_on TIMESTAMPTZ NOT NULL,

    accepter INTEGER REFERENCES device (_id),

    enrollment_state enrollment_state NOT NULL,
    info_accepted pki_enrollment_info_accepted,
    info_rejected pki_enrollment_info_rejected,
    info_cancelled pki_enrollment_info_cancelled,

    UNIQUE(organization, request_id)
);