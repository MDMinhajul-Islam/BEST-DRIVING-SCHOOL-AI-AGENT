# Booking integration plan — design only

Caller → Retell Conversation Flow → manually configured Booking Specialist →
Retell Custom Function → our approved Backend API → school scheduling system.

Proposed backend endpoints, not implemented in this scraping task:

- `POST /api/retell/check-availability`
- `POST /api/retell/create-booking`
- `POST /api/retell/find-booking`
- `POST /api/retell/reschedule-booking`
- `POST /api/retell/cancel-booking`

These are proposed paths on our future backend, not claims about APIs on the
school website. Restricted school routes are not integration contracts.

Before building, obtain explicit school API access and documented capabilities.
Map reviewed catalog package IDs to authoritative scheduling service IDs. Confirm
location rules and the school's timezone. Define verified identity and consent
requirements, service-specific cancellation policy and failure/escalation behavior.

Check availability, offer only returned slots, repeat critical service/student/
date/time/location details, obtain confirmation, and then call creation. A
reschedule checks the replacement slot and applies the change atomically. A
cancellation follows the approved service policy and does not promise a refund.

The backend should authenticate Retell requests using the current documented
supported mechanism, protect credentials, validate payloads, enforce idempotency,
limit authorized account access and emit audited structured results. Confirm
current Retell function documentation in the implementation phase; no unverified
platform-specific payload or signature behavior is assumed here.

Test empty availability, races, wrong identity, duplicate submissions, stale
booking version, provider downtime and uncertain write outcomes in an approved
sandbox. A prototype mock may be agreed in that phase but is not supplied or
presented as live school functionality here.

The manually designed Retell node must consume tool success/failure results.
Static scrape knowledge supports service selection and preparation, not the
execution of booking actions.
