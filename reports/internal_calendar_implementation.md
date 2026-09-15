# Internal calendar and admin implementation

Implemented September 15, 2026 on the existing provider/service/SQLite/FastAPI foundation.

## Result

Internal provider, empty-by-default calendar, admin-defined rules/capacity, blackouts, atomic multi-session groups, transactional conflict prevention, scoped five-operation API and authenticated same-image admin dashboard are implemented. Mock remains available for fixture testing. Cal.com code is retained and stays disabled. No Retell, Dokploy, external school system or Cal.com service was modified.

The internal schema and algorithms are documented in `docs/internal_calendar_architecture.md`; admin operation/security in `docs/admin_dashboard_guide.md`; unchanged Retell-facing transport in `docs/retell_booking_api_contract.md`.

## Safety decisions

- No recurring hours, capacity, instructor, vehicle, branch or holiday data is seeded or assumed.
- Canonical slugs are internal package identities and never described as school backend IDs.
- Admin must supply positive capacity before a rule can exist.
- Blackouts supersede recurring rules.
- SQLite `BEGIN IMMEDIATE` revalidates capacity during create/reschedule.
- Internal group/session/generic appointment/history inserts share one atomic create transaction.
- Cancellation releases capacity without payment/refund behavior.
- Existing body-derived durable idempotency remains backwards-compatible; no unsafe write retry was added.
- Operational customer name/email is stored for admin use; never returned through broad listing to unauthenticated clients.
- Admin uses PBKDF2 password hashes, signed HttpOnly/SameSite sessions, HTTPS-secure cookies by default and CSRF headers.

## Verification

Automated tests cover empty startup, catalog readiness, slot generation, blackout override, capacity one/two, concurrent conflict, atomic multi-session commit/rollback, adult/teen/road rules, unresolved-package block, DST timestamps, create/find/reschedule/cancel, release/history, idempotency, restart persistence, provider configuration/health, login/CSRF, admin rule edit, admin reschedule/cancel, booking detail and local-time blackout management. The full suite passes 132 tests. The production image `best-driving-school-booking-api:internal-local` built successfully. A container acceptance run passed internal health/authentication, empty initial availability, admin rules, blackouts, booking visibility, create/find/reschedule/cancel and named-volume persistence after container recreation.

Known limits: one replica/worker with local SQLite; no resource/instructor assignment; no manual booking creation; no payment model; no stale-lock reconciliation UI; admin list is a chronological schedule rather than a graphical week grid; future PostgreSQL redesign is required for horizontal scale.
