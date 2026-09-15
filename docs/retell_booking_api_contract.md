# Retell booking wrapper API contract

Prepared September 15, 2026 for later manual Retell wiring. The intended deployment provider is `internal`; the same contract continues with `mock`. The base URL is pending Dokploy domain configuration. All timestamps are UTC ISO 8601 and the business timezone is America/Chicago.

## Transport and authentication

- Health: unauthenticated `GET {BASE_URL}/api/health`; it performs no write.
- Booking: `POST {BASE_URL}/api/booking/{operation}`, JSON, private `X-Retell-Tool-Secret`, and trusted `X-Booking-Scope` (16–128 letters/digits/underscore/hyphen). Preserve one scope across related demo operations. It is integration isolation, not identity verification.
- Maximum body is 64 KiB; unknown fields are rejected. Direct arguments or Retell envelope `{ "name":"...", "call":{}, "args":{...} }` work. Call metadata is discarded. No CORS is configured because this is server-to-server.

Unauthorized/missing scope returns 401. Unknown operation returns 404; malformed transport/schema returns 400 or 413; infrastructure failures return 503. Domain failures intentionally use HTTP 200 with `success:false` so Retell can branch consistently. Always inspect body fields.

Success includes `success:true`, `mode`, `booking_provider` (`internal` for the intended deployment), `production:false`, `synthetic`, `demo:true`, and `booking_confirmed`. Failure includes `success:false`, `booking_confirmed:false`, `error_code`, and `user_safe_message`. Only provider `accepted` confirms. Pending/partial/unknown never confirms. Cancellation reports `refund_issued:false` and does not decide a refund.

## Operations

**check_availability — `/check-availability`.** Requires `package_id` and `preferred_date` (`YYYY-MM-DD`). Optional `session_duration_minutes` (allowed plan integer), `preferred_time_window` (`morning|afternoon|evening`), and `timezone` (exactly `America/Chicago`). Success adds package/timezone, `scheduling_required`, integer `session_plan`, `session_count_required`, and identical `available_slots`/`slots`. Each slot has `slot_ref`, `slot_id`, `start`, `end`, `duration_minutes`. Refs are opaque, scoped and expire after five minutes. Availability never confirms a booking.

**create_booking — `/create`.** Requires `package_id`, `slot_ids` in exact plan order, and `customer` exactly `{name,email}`. Use synthetic contact data during testing. Confirmed internal success adds `booking_group_id`, `package_booking_status:"confirmed"` and `sessions`, each with index, internal appointment_id, start, end and booking_status. A single session also appears at top level. Internal multi-session creation is atomic, so a conflict leaves no partial group. Legacy provider partial responses remain possible and set `human_review_required:true`; never retry automatically.

**find_booking — `/find`.** Requires `appointment_id`. Success adds appointment_id, start, end, booking_status and booking_confirmed. Only a known internal appointment in the same scope/mode is returned; no email, phone or provider-ID enumeration.

**reschedule_booking — `/reschedule`.** Requires `appointment_id` and a fresh compatible `slot_ref`. Success has find fields with new times. Confirm only when success and booking_confirmed are true; never automatically retry an unknown write.

**cancel_booking — `/cancel`.** Requires `appointment_id`. Completion requires `success:true` and `booking_status:"cancelled"`; response has `booking_confirmed:false` and `refund_issued:false`.

## Retell conditions

- Package confirmed only when `success`, `booking_confirmed`, package status confirmed, correct session count and every session confirmed with an internal ID.
- Find/reschedule confirmed when `success && booking_confirmed`.
- Cancellation completed when `success && booking_status == "cancelled"`.
- Treat `success:false`, missing/partial sessions, pending, OUTCOME_UNKNOWN, timeout, 401, 4xx or 5xx as failure. Use the safe message and staff fallback.
- Set Retell timeout above the backend/provider window. Do not retry create/reschedule/cancel after client timeout: it can conceal a provider outcome, and durable locks intentionally prevent duplication.

Plans: adult 2/4/6/8/10 hours map to 1/2/3/4/5 × 120 minutes; known teen seven-hour plans map to 120+120+120+60; road-test-only maps to 30. Online needs no appointment. Practice + Road Test and PTDE allocation remain staff review. Retell is not wired by this document.
