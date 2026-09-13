# Manual Retell HTTP wiring — Phase F

Retell was not changed. Configure tools manually only after the backend has an actual HTTPS domain and the desired mode has been reviewed. Existing historical Phase D/E artifacts remain intact; this guide supplies the new wrapper contract.

All five operations are POST requests to your deployed backend:

| Tool | Path | Required JSON arguments |
|---|---|---|
| check_availability | /api/booking/check-availability | package_id, preferred_date |
| create_booking | /api/booking/create | package_id, slot_ids, customer |
| find_booking | /api/booking/find | appointment_id |
| reschedule_booking | /api/booking/reschedule | appointment_id, slot_ref |
| cancel_booking | /api/booking/cancel | appointment_id |

Set private header `X-Retell-Tool-Secret` to the server secret (at least 32 characters). Set `X-Booking-Scope` from trusted call setup or the test harness: an opaque 16–128 character value containing letters, digits, underscore, or hyphen. Preserve the same scope for related operations and later authorized lookup. It is integration-level demo isolation, not customer identity verification. Never let the language model choose a different scope or arbitrary email. A production customer verification mechanism remains separate future work. Provider keys stay only in backend environment variables.

Direct argument objects and Retell envelopes `{ "name": "tool_name", "call": {}, "args": { ... } }` are supported. Call metadata is discarded. Unknown argument fields are rejected; maximum request size is 64 KiB. Dates must be explicit `YYYY-MM-DD`. Optional availability fields: `session_duration_minutes` (integer in that package plan), `preferred_time_window` (morning/afternoon/evening), and `timezone` (America/Chicago only). Natural-language time resolution belongs in the conversation before the tool call.

Example availability arguments:

```json
{"package_id":"road_test_road_test_only","preferred_date":"2035-10-01","session_duration_minutes":30,"timezone":"America/Chicago"}
```

Availability returns `available_slots` (also `slots`), each with `slot_ref` (also `slot_id`), timezone-aware UTC `start`/`end`, and duration. It also returns the complete `session_plan` and required count. Slots are opaque, scoped, provider-mode-bound, and expire after five minutes. Check each required duration and collect exactly the returned references in plan order. Never manufacture a timestamp or slot reference.

Create uses `slot_ids` as an array of those references and `customer` as exactly `{ "name": "BDS AI TEST ...", "email": "configured private synthetic test email" }`. The harness supplies attendee data; the model does not collect extra personal information. No licenses, dates of birth, payment data, or real customer records are accepted. Example schemas: slot_ids is an array of strings; customer is an object requiring name/email with additional properties disabled; all other required arguments in the table are strings.

Create results include `sessions` with index, internal appointment_id, start, end, booking_status. A one-session result also exposes appointment_id/start/end/booking_status at the top level. References start with `MOCK-` or `CAL-DEMO-`; raw Cal booking UIDs stay server-side. Find, reschedule, and cancel only accept a known internal appointment belonging to the same trusted scope and mode. Lookup never searches by phone or email and never enumerates Cal.com bookings. Reschedule uses one selected `slot_ref` with the same session duration. Cancel reports `refund_issued=false`.

Each response identifies mode, provider, demo=true and production=false. Confirm a package only when `success=true`, `booking_confirmed=true`, `package_booking_status=confirmed`, and all required sessions have returned internal references and confirmed statuses. A successful availability request is never a booking. For session lookup/change, inspect its explicit booking_confirmed and booking_status. Cancellation means cancelled, not booked. Pending is not confirmed. Business failures return safe JSON; authentication failures are HTTP 401. Do not speak raw provider exceptions or infer confirmation from HTTP 200.

Server-owned idempotency records the complete normalized operation; repeated payloads reuse the existing result and refresh local status after later changes. Do not pass a model-created idempotency key. Partial packages retain each accepted session and return human_review_required; staff must reconcile rather than automatically cancel accepted sessions. Uncertain outcomes prohibit duplicate writes. Wire these outcomes to the existing staff-review path in booking node 06; retain earlier eligibility, package selection, and business rule guards. Do not use model extraction to invent appointment IDs or claim the demo provider is the school calendar.
