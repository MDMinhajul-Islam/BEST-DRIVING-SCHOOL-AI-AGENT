# Operational data requirements — future phase

Static knowledge covers public services, package prices, requirements, FAQ,
policy text, office contacts and service areas. It cannot establish current
availability, bookings, enrollment records, student accounts or payment status.
Do not use scraped upcoming batches, form date fields or stale marketing text
to offer a slot.

Future tools must use an explicitly approved school integration. Obtain the
school's scheduling vendor/API documentation, credentials, sandbox, supported
service identifiers, instructor/resource rules and booking permissions before
implementation. Do not guess private routes or reverse-engineer payment flows.

| Tool | Required inputs to agree with school | Required result |
| --- | --- | --- |
| check_availability | Approved service/package ID, location/resource, date window and timezone | Open slot IDs, timestamps, timezone, expiry/version; explicit empty result |
| create_booking | Verified minimum student/contact fields, service, returned slot ID, confirmed caller consent, idempotency key | Persisted booking ID and confirmed details; structured conflict/error otherwise |
| find_booking | Approved booking reference and identity-verification proof | Only authorized booking details; no unrestricted phone/email enumeration |
| reschedule_booking | Verified booking ID, checked replacement slot, caller confirmation, idempotency key and booking version | Atomic updated record; preserve original on failure |
| cancel_booking | Verified booking ID, confirmed request, approved applicable policy, reason if required and idempotency key | Actual cancellation status; no guessed refund result |

Policy decisions needed: cancellation/rescheduling windows and fees by service,
refund handling, payment requirements for booking, guardianship/teen enrollment,
required eligibility documents, pickup/training locations, resource conflicts,
timezone, daylight-saving behavior and confirmation delivery. The current static
corpus does not settle all these questions.

Identity verification is required before private lookup or changes. A provided
name, phone number or caller ID alone is not assumed to be sufficient. Agree the
verification procedure, least-privilege access, retention and audit requirements
with the school. Payment-card data and passwords must not enter voice variables.

Return explicit status, stable error codes, user-safe message and authoritative
details. Backend timeouts do not mean success. Handle uncertain write outcomes
through idempotent retry/status lookup; availability can change between check
and booking. The voice agent confirms success only after authoritative success.

Course access, payment disputes, certificate corrections and refund decisions
need authenticated support integrations or a human escalation process. No such
operations exist in this repository.
