# Phase F — Cal.com demo booking integration

Date: September 13, 2026. This phase implements backend code and deployment artifacts; it does not deploy a public service or modify Retell.

| Item | Result |
|---|---|
| Provider | Cal.com API v2, internship DEMO only; existing school adapter preserved |
| Default mode | mock, durable duration-aware synthetic provider |
| Other modes | calcom_test; calcom_live additionally gated; credentials alone never enable writes |
| Business timezone | America/Chicago; UTC ISO timestamps and DST-aware date boundaries |
| Required event types | 120, 60, 30 minutes; all actual IDs currently null / NOT READY |
| Public event discovery | HTTP 200; two unrelated 45-minute Northstar events, unchanged |
| Private provider reads | NOT RUN; no API key configured |
| Actual Cal create / reschedule / cancel | NO / NO / NO |
| HTTP wrapper | Implemented, authenticated and verified locally; not deployed |
| Dokploy | Backend Application Dockerfile provided; frontend Application deferred |
| Docker build | NOT RUN: CLI present, Docker Desktop Linux engine unavailable |
| Retell | Unchanged; manual wiring guide supplied |
| Tests | 104 passed: all previous 72 plus 32 new integration tests |

## Package readiness

Five verified adult driving plans and both known seven-hour teen plans map to 120-minute sessions with any verified 60-minute remainder. Teen plans are 120/120/120/60. Road-test-only maps to a 30-minute allocation including reset/system buffer. These are DEMO MAPPING READY, conditional on actual Cal event setup. Adult online courses require no appointment. PTDE and practice + test remain STAFF REVIEW REQUIRED; observation and classroom scheduling remain outside scope. `data/structured/calcom_event_type_map.json` records every canonical package, without inventing event IDs.

## Operations and safety behavior

All five adapter operations and HTTP routes are implemented: check availability, create, known scoped find, reschedule, and cancel. The original BookingAdapter/Mock/school-read interfaces and source artifacts remain available. The wrapper uses BookingService to bridge normalized tool requests to the providers; PersistentMockBookingAdapter extends the existing mock while adding durable, duration-aware behavior. The existing school adapter still cannot perform production lookup or writes.

Slots are opaque, scope/mode/package/duration-bound and expire after five minutes. Every package session is selected and revalidated before writes. SQLite stores internal appointment references, provider UIDs, action fingerprints, safe results, audit metadata and durable operation locks. Attendee fields are not persisted in the appointment/audit tables. Server-owned action fingerprints prevent replayed writes after restart. Provider UIDs never appear in wrapper responses; lookup accepts only known internal references in the same scope and environment.

Provider accepted status, valid UID, expected start, and duration are required for confirmation. Pending and malformed responses do not confirm. A race returns SLOT_UNAVAILABLE when evidenced; uncertain writes remain OUTCOME_UNKNOWN. Multi-session packages are separate provider transactions. Accepted sessions are persisted before proceeding; partial failures require staff reconciliation and retain their locks, with no automatic cancellation or rollback. Cancellation does not issue a refund. Locks and pending ledger entries are deliberately conservative after crashes; manual reconciliation is necessary before unlocking.

Routes require a private X-Retell-Tool-Secret and trusted X-Booking-Scope. The scope is demo integration isolation, not production customer authentication. Requests are strictly bounded and reject unknown fields. Provider keys stay server-side; responses and audit rows exclude provider bodies and attendee PII. Access logs are disabled by the deployment command. Test attendee names must start with BDS AI TEST; real Cal demo writes additionally require the privately configured test email. Prices and regulatory decisions remain in existing authoritative project data.

## Verification evidence

Executed `.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests`: 104 tests passed. Coverage includes the full previous preservation checks; plan mapping and unresolved guards; timezone/DST handling; header authentication; scope and slot isolation; direct/Retell-envelope requests; body limits; all five mock operations across SQLite restart; duplicate/concurrent requests; prevalidation before writes; partial failure without rollback; uncertain write replay prevention; audit redaction; Cal endpoint version headers; minimal attendees; accepted/pending responses; conflict/timeout/malformed responses; mapping/write/live gates; payment/extra-field/double-buffer guards; all five Cal adapter operations with HTTP fixtures; Cal-to-wrapper normalization without UID leakage. Tests use synthetic fixtures, not live Cal writes. A TestClient dependency deprecation warning is present; it did not affect results.

Local authenticated HTTP smoke testing also created a six-hour adult package as three persistent 120-minute mock sessions. `git diff --check` passed. The local Docker engine was unavailable, so no container build or health claim is made. A public domain, actual event setup, credentialed availability validation, and explicitly enabled synthetic Cal transactions remain operator steps.

## Official API sources

Verified endpoint-specific versions: [slots](https://cal.com/docs/api-reference/v2/slots/get-available-time-slots-for-an-event-type) 2024-09-04; [event types](https://cal.com/docs/api-reference/v2/event-types/get-an-event-type) 2024-06-14; [create](https://cal.com/docs/api-reference/v2/bookings/create-a-booking), [find](https://cal.com/docs/api-reference/v2/bookings/get-a-booking), [reschedule](https://cal.com/docs/api-reference/v2/bookings/reschedule-a-booking), and [cancel](https://cal.com/docs/api-reference/v2/bookings/cancel-a-booking) 2026-02-25. Deployment configuration follows [Dokploy Application build types](https://docs.dokploy.com/docs/core/applications/build-type) and [Application volume mounts](https://docs.dokploy.com/docs/core/applications/advanced).

Primary deliverables: `docs/calcom_setup_guide.md`, `docs/retell_calcom_tool_wiring.md`, and this report. Deployment details: `docs/dokploy_application_deployment.md`. No secrets, supplied email, or test calendar mutations were committed.
