# Dokploy Application deployment

Deploy the backend as a Dokploy **Application** using this repository's root `Dockerfile`, build context `.`, container port 8000. No Compose service is needed. The frontend will be created later and deployed as its own Application.

Dokploy supports a [Dockerfile build type](https://docs.dokploy.com/docs/core/applications/build-type). Supply environment variables privately in the backend Application using `.env.example` as the field list. Start with BOOKING_MODE=mock, a fresh private RETELL_TOOL_SECRET of at least 32 characters, BOOKING_DB_PATH=/app/runtime/booking.sqlite3, and both Cal write/live gates false. Keys are runtime configuration, not build arguments. The backend does not automatically load a local .env file.

Add a persistent named volume mounted at `/app/runtime` using [Application volume mounts](https://docs.dokploy.com/docs/core/applications/advanced). Ensure its files are writable by container user UID 10001. Keep one replica, one worker, and one durable database volume; SQLite is not configured for distributed replicas. Back up the whole runtime volume including SQLite sidecars, preferably with the process stopped or a consistent SQLite backup. See [Dokploy volume backups](https://docs.dokploy.com/docs/core/volume-backups). Losing this volume loses retry protection and appointment mappings.

Configure the actual backend [domain and HTTPS](https://docs.dokploy.com/docs/core/domains) to port 8000. Health path: GET /api/health, which returns only {"status":"ok"}. The Dockerfile has the same health check and starts uvicorn with access logs disabled. HTTP API documentation and cross-origin browser access are disabled. A future frontend should use its own server-side proxy; never ship the Retell secret or Cal key to a browser.

After deployment, verify health over HTTPS, wrong-secret rejection, authenticated mock availability, create/find/reschedule/cancel, and restart persistence. Use only synthetic records. Then follow the Cal.com guide for reviewed event IDs and explicit test enablement. No public domain is configured or deployment performed by this phase.

Local execution after installing requirements and setting private environment variables:

```powershell
.venv\Scripts\python.exe -m uvicorn src.routes.booking:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests
```

The container targets Python 3.12; local verification uses Python 3.14. Container build verification is a separate deployment check if Docker is unavailable on the workstation. A missing secret intentionally prevents startup. A fresh mount may need an operator permission adjustment before the first startup.
