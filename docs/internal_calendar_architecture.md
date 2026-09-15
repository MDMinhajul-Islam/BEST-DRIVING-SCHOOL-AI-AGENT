# Internal calendar architecture

The internal provider is the intended single-instance scheduling source for the Best Driving School demo/internal system. It preserves the five Retell-facing routes and does not call Cal.com or the school website. Cal.com remains optional and disabled.

## Provider selection

| Provider | BOOKING_PROVIDER | BOOKING_MODE | Behavior |
|---|---|---|---|
| Persistent fixture | mock | mock | Synthetic fixed slots for tests |
| Internal calendar | internal | internal | Admin-configured availability and SQLite bookings |
| Cal.com demo | calcom | calcom_test/calcom_live | Existing explicitly gated future adapter |

Provider/mode mismatches fail startup. Internal mode also fails startup unless admin username, PBKDF2 password hash and a 32+ character session secret exist. `SEED_DEMO_DATA` defaults false and the application never seeds schedules or bookings.

## SQLite model

All tables use the existing database at `/app/runtime/booking.sqlite3`. Initialization uses idempotent `CREATE TABLE/INDEX IF NOT EXISTS` and never deletes rows.

- `internal_services`: canonical internal package IDs/names, session plans and auto-schedulable flag. It is synchronized from the canonical catalog; observed website product IDs are not used.
- `availability_rules`: package or wildcard scope, weekday 0–6, local start/end, effective dates, explicit positive capacity, active flag and timestamps.
- `blackouts`: package/wildcard, absolute UTC interval, optional note and active flag.
- `booking_groups`: internal group ID, API scope, package, operational customer name/email, group status and timestamps.
- `internal_sessions`: internal provider UID, group/reference, package, UTC interval, accepted/cancelled state and timestamps.
- `internal_history`: timestamp, action, object type/ID and safe JSON metadata.
- Existing `slots`, `appointments`, `actions`, `locks` and `audit` retain opaque API refs, scoped lookup, idempotent actions and safe integration audit.

## Availability and capacity

A fresh database contains services but **zero availability rules and zero slots**. Slots are generated only from active admin rules whose weekday/effective dates cover the requested date and whose positive capacity is explicit. Times are interpreted in America/Chicago and returned as UTC ISO timestamps. Each service duration tiles the configured local window. DST conversion uses `zoneinfo`.

Active package/wildcard blackouts override rules when intervals overlap. Accepted internal sessions consume capacity; cancelled sessions release it. Multiple matching rules do not imply unlimited capacity. The implementation uses the capacity of a matching explicit rule and counts all overlapping accepted sessions.

## Transaction safety

Availability reads are advisory. Internal create starts `BEGIN IMMEDIATE`, revalidates every requested interval against rules, blackouts and capacity, then inserts one booking group, every session, the generic appointment mappings and history. Any conflict raises the existing `SLOT_UNAVAILABLE` error and rolls back everything. This preserves the public error contract while providing SLOT_CONFLICT semantics.

Reschedule uses `BEGIN IMMEDIATE`, requires an accepted known session, preserves duration, revalidates the replacement while excluding the current session, updates only after success, and records old/new time history. Cancel changes accepted to cancelled, records timestamp/history, releases capacity, and marks a group cancelled when no active session remains. It never records or implies payment/refund state.

The existing server-owned normalized action hash remains idempotency authority for create/reschedule/cancel and requires no new client header. Same requests reuse results; unknown writes remain conservatively blocked. Internal group creation is atomic, unlike the intentionally conservative external-provider multi-write behavior.

## Package rules and limits

Adult 2/4/6/8/10-hour plans use 1/2/3/4/5 × 120 minutes. Both known teen seven-driving-hour plans use 120+120+120+60; observation is separate. Road-test-only uses 30 minutes (20 service + 5 reset + 5 buffer). Online is non-schedulable. Practice + Road Test and unresolved PTDE allocation remain non-auto-schedulable and cannot receive active package-specific rules through admin.

This SQLite MVP requires one application replica and one worker. For horizontal scale, move transactional scheduling to a shared database such as PostgreSQL and review locks/constraints. Instructor, vehicle, resource pool, branch/holiday assignment and payment status are deliberately absent until authoritative configuration exists.
