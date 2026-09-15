# Booking backend final audit and deployment readiness

Audit date: September 15, 2026. Actual implementation was inspected. No Retell, Cal.com or production school system was modified.

## Status

**Backend READY; Docker VERIFIED; Dokploy NOT DEPLOYED.** Provider is mock. Local Uvicorn and the production container passed health, authentication, all five operations and SQLite persistence across process/container recreation.

| Area | Actual implementation | Result |
|---|---|---|
| Entrypoint/runtime | `src.routes.booking:create_app`; FastAPI/Uvicorn, Python 3.12 image | PASS |
| Routes | POST `/api/booking/check-availability`, `/create`, `/find`, `/reschedule`, `/cancel` | PASS |
| Health | public GET `/api/health`; service/provider/timezone, no write/secret | PASS |
| Authentication | constant-time secret plus bounded trusted scope | PASS |
| Validation | 64 KiB limit, strict fields/envelope, package/date/timezone/duration/customer/ref checks | PASS |
| Responses/safety | safe normalized results, accepted-only confirmation, provider UID hidden | PASS |
| Providers | original abstraction, persistent mock, gated Cal.com v2 | PASS |
| SQLite | idempotent schema, WAL, transactions, durable actions/locks/audit | PASS |
| Timezone | America/Chicago business dates, UTC timestamps, DST-aware bounds | PASS |
| Logging/CORS | access log disabled; no exception/provider body logging; no CORS | PASS |
| Container | non-root `booking` user, `/app/runtime`, 8000, healthcheck, one worker, exact pins | PASS |
| Compose | absent and unnecessary for Dokploy Application mode | PASS |

Health now reports deployment state, `.env.example` defaults consistently to provider/mode mock, and configuration rejects mismatches. `requirements.deploy.txt` gives exact production dependency versions.

Availability validates package/date/duration and returns provider slots as expiring scoped refs. Create validates all sessions before writes and confirms only complete accepted results. Find accepts only known internal same-scope/mode references. Reschedule requires a compatible returned slot. Cancel requires explicit cancelled status and reports no refund. Ambiguous and partial writes remain durably locked for staff reconciliation without automatic retries or rollback.

Adult plans use 1–5 × 120-minute sessions; known teen plans use 120+120+120+60 without applying this to observation; road-test-only is 30 minutes (20+5+5). Practice + Road Test and PTDE remain staff review. Online is not scheduled.

## Verification

- Tests: **111/111 passed** (current rebased Python suite, including six frontend voice-route tests).
- Local Uvicorn HTTP: health, unauthorized 401, availability, create, find, reschedule and cancel PASS.
- Process restart using same temporary SQLite file: lookup/reschedule/cancel PASS.
- `git diff --check` and compile checks: PASS.
- Docker engine: PASS, Linux/amd64 engine 29.6.2. Production image `best-driving-school-booking-api:local` built successfully from Python 3.12 slim; size 52,568,665 bytes; exposed `8000/tcp`; runtime user `booking`.
- Dokploy: BLOCKED. Browser inventory contains Retell only; repository has no Dokploy URL/project/application ID or established API domain. No domain was invented.
- Container HTTP: health 200, unauthorized 401, validation, five operations and explicit no-refund cancellation PASS. Container recreation with the same named `/app/runtime` volume preserved the appointment. Temporary container/volume were removed after verification.
- HTTPS/public smoke: NOT RUN because Dokploy was explicitly excluded from this phase.

Dokploy target: `best-driving-school-booking-api`, root Dockerfile/context, port 8000, `/api/health`, one replica/worker, named volume `/app/runtime`, database `/app/runtime/booking.sqlite3`, TLS at Dokploy/Traefik. Remaining inputs are authenticated Dokploy URL/session or API access, target project/server, established domain/subdomain, and a private tool secret entered into Dokploy. Cal.com stays disabled and is not required for first Retell integration.
