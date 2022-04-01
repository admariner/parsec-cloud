-- Parsec Cloud (https://parsec.cloud) Copyright (c) AGPLv3 2016-2021 Scille SAS


-- pki_certificate_submitted
INSERT INTO pki_enrollment(_id, organization, request_id, submitter_der_x509_certificate, submit_payload_signature, submit_payload, enrollment_state, submitted_on) VALUES(
    6,
    10,
    '6ecd8c99-4036-403d-bf84-cf8400f67836',
    E'<certificate>',
    E'<signature>',
    E'<payload>',
    'SUBMITTED',
    '2021-10-29 11:30:16.791954+02'
);

-- pki_certificate_cancelled
INSERT INTO pki_enrollment(_id, organization, request_id, submitter_der_x509_certificate, submit_payload_signature, submit_payload, enrollment_state, submitted_on, info_cancelled.cancelled_on) VALUES(
    7,
    10,
    '6ecd8c99-4036-403d-bf84-cf8400f67837',
    E'<certificate>',
    E'<signature>',
    E'<payload>',
    'CANCELLED',
    '2021-10-29 11:30:16.791954+02',
    '2021-10-29 11:30:16.791954+02'
);

-- pki_certificate_rejected
INSERT INTO pki_enrollment(_id, organization, request_id, submitter_der_x509_certificate, submit_payload_signature, submit_payload, enrollment_state, submitted_on, info_rejected.rejected_on) VALUES(
    8,
    10,
    '6ecd8c99-4036-403d-bf84-cf8400f67838',
    E'<certificate>',
    E'<signature>',
    E'<payload>',
    'REJECTED',
    '2021-10-29 11:30:16.791954+02',
    '2021-10-29 11:30:16.791954+02'
);


-- pki_certificate_accepted
INSERT INTO pki_enrollment(_id, organization, request_id, submitter_der_x509_certificate, submit_payload_signature, submit_payload, enrollment_state, submitted_on, info_accepted.accepted_on, info_accepted.accepter_der_x509_certificate, info_accepted.accept_payload_signature, info_accepted.accept_payload) VALUES(
    9,
    10,
    '6ecd8c99-4036-403d-bf84-cf8400f67839',
    E'<certificate>',
    E'<signature>',
    E'<payload>',
    'ACCEPTED',
    '2021-10-29 11:30:16.791954+02',
    '2021-10-29 11:30:16.791954+02',
    E'<certificate>',
    E'<signature>',
    E'<payload>'
)

