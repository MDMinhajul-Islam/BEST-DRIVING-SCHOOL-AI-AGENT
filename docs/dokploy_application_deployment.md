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

### Frontend Application

Deploy the frontend as a separate Dokploy Application from the same `main` branch. Set the build context/root directory to `frontend`, use Nixpacks, and route the domain to container port `3000`. The committed `.nvmrc` and `package.json` require Node `22.22.0` or newer. Set:

```dotenv
NEXT_PUBLIC_VOICE_DEMO_MODE=true
NEXT_PUBLIC_ADMIN_URL=https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io/admin
VOICE_BACKEND_URL=https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io
VOICE_PROXY_SECRET=<same private server-only voice broker value, when voice is enabled>
SITE_ORIGIN=https://minhaj-bds-frontend-7wmdcd-5ad051-206-189-183-167.sslip.io
```

`NEXT_PUBLIC_ADMIN_URL` is a public navigation URL. `VOICE_PROXY_SECRET` remains server-only despite being configured on the frontend Application because Next.js does not expose variables without the `NEXT_PUBLIC_` prefix.

### Isolated voice broker Application

Create a third Dokploy Application from the same repository and `main` branch. Use Dockerfile build mode with context `.` and Dockerfile `Dockerfile.voice`, route its HTTPS domain to container port `8000`, and use `/api/health` as its health check. Keep one worker; the in-process call-creation limiter assumes a single replica.

Set only these server-side values on the voice broker:

```dotenv
RETELL_API_KEY=<private Retell API key>
RETELL_AGENT_ID=<published Best Driving School agent ID>
VOICE_PROXY_SECRET=<private random value of at least 32 characters>
```

Copy the API key from the Retell dashboard API Keys area and the published agent ID from the Best Driving School agent page. Never place either value in a `NEXT_PUBLIC_*` variable. Set the frontend `VOICE_BACKEND_URL` to the broker's HTTPS origin, set the same `VOICE_PROXY_SECRET`, and change `NEXT_PUBLIC_VOICE_DEMO_MODE=false` only after the broker health and authenticated session path pass.

## Persistence, networking and verification

Create a named volume at `/app/runtime`; SQLite is `/app/runtime/booking.sqlite3`. Schema creation is idempotent and does not reset data. Ensure UID 10001 can write. Use one replica because SQLite is not configured for distributed writers. Back up the entire volume, including SQLite sidecars, with a consistent backup or while stopped.

Use the project's established API subdomain when supplied; do not invent one. Route it to port 8000 and enable HTTPS. No public URL is hardcoded. Use Dokploy's normal automatic restart policy; avoid overlapping instances for this SQLite deployment.

Verify `GET https://<domain>/api/health` returns 200 with service, provider `internal`, and America/Chicago. Verify unauthorized booking returns 401. With synthetic data run availability → create → find → availability → reschedule → cancel, restart the Application, then find the same persisted cancelled appointment. Inspect responses/logs for no secret or provider UID.

See [Retell contract](retell_booking_api_contract.md). Dokploy references: [Dockerfile build](https://docs.dokploy.com/docs/core/applications/build-type), [volumes](https://docs.dokploy.com/docs/core/applications/advanced), [backups](https://docs.dokploy.com/docs/core/volume-backups), [domains](https://docs.dokploy.com/docs/core/domains).

## Current status

The backend and frontend are deployed as separate Dokploy Applications. Backend health reports provider `internal` and America/Chicago. Availability remains empty until staff creates a positive-capacity rule in the authenticated dashboard. Retell remains manually configured and unchanged by deployment.
