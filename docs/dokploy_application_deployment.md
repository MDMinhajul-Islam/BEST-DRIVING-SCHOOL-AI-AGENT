# Dokploy Application deployment

## Exact first-deployment configuration

| Setting | Value |
|---|---|
| Application name | `best-driving-school-booking-api` |
| Source branch | `main` |
| Build method | Dockerfile |
| Dockerfile / context | `Dockerfile` / `.` |
| Internal port | `8000` |
| Health path | `/api/health` |
| TLS | Dokploy/Traefik HTTPS termination |
| Persistent mount | named volume → `/app/runtime` |
| Replicas/workers | 1 / 1 |
| CORS | none; server-to-server API |

The image starts production Uvicorn on `0.0.0.0:8000`, disables access logs, runs as UID 10001, and installs exact pins from `requirements.deploy.txt`. It includes a container health check. No Compose file is required. The internal Admin Dashboard is served by this same backend Application at `/admin`; the existing public website frontend remains separate.

## Environment

```dotenv
BOOKING_PROVIDER=internal
BOOKING_MODE=internal
BOOKING_DB_PATH=/app/runtime/booking.sqlite3
RETELL_TOOL_SECRET=<private random value of at least 32 characters>
CALCOM_API_BASE_URL=https://api.cal.com
CALCOM_TIMEZONE=America/Chicago
CALCOM_WRITE_ENABLED=false
CALCOM_LIVE_ENABLED=false
CALCOM_API_KEY=
CALCOM_EVENT_TYPE_DRIVING_120=
CALCOM_EVENT_TYPE_DRIVING_60=
CALCOM_EVENT_TYPE_ROAD_TEST_30=
CALCOM_TEST_EMAIL=
ADMIN_USERNAME=<private admin username>
ADMIN_PASSWORD_HASH=<private PBKDF2 hash>
ADMIN_SESSION_SECRET=<private random value of at least 32 characters>
ADMIN_COOKIE_SECURE=true
SEED_DEMO_DATA=false
```

The backend does not load `.env` automatically. Keep API/admin secrets only in private configuration. Provider and mode must match. Cal fields stay blank/false; production school writes are independently blocked. No availability is seeded. Admin is served at `/admin`.

## Persistence, networking and verification

Create a named volume at `/app/runtime`; SQLite is `/app/runtime/booking.sqlite3`. Schema creation is idempotent and does not reset data. Ensure UID 10001 can write. Use one replica because SQLite is not configured for distributed writers. Back up the entire volume, including SQLite sidecars, with a consistent backup or while stopped.

Use the project's established API subdomain when supplied; do not invent one. Route it to port 8000 and enable HTTPS. No public URL is hardcoded. Use Dokploy's normal automatic restart policy; avoid overlapping instances for this SQLite deployment.

Verify `GET https://<domain>/api/health` returns 200 with service, provider `internal`, and America/Chicago. Verify unauthorized booking returns 401. With synthetic data run availability → create → find → availability → reschedule → cancel, restart the Application, then find the same persisted cancelled appointment. Inspect responses/logs for no secret or provider UID.

See [Retell contract](retell_booking_api_contract.md). Dokploy references: [Dockerfile build](https://docs.dokploy.com/docs/core/applications/build-type), [volumes](https://docs.dokploy.com/docs/core/applications/advanced), [backups](https://docs.dokploy.com/docs/core/volume-backups), [domains](https://docs.dokploy.com/docs/core/domains).

## Current status

Local Python and production-container verification passed internal health/authentication, empty-by-default availability, admin rule and blackout control, all five booking operations, dashboard visibility and persistence after container recreation. Image `best-driving-school-booking-api:internal-local` built successfully, exposes port 8000 and runs as `booking`. Dokploy was intentionally not deployed in this phase; domain, volume, private admin credentials and public HTTPS checks remain deployment steps. Retell remains unchanged.
