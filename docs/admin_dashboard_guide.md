# Internal calendar admin dashboard

Admin URL: `https://<api-domain>/admin` (local verification uses `http://127.0.0.1:18082/admin`). It is served by the same FastAPI image only in internal mode. The HTML shell is public but every data/action endpoint requires login; it contains no operational data or secrets before authentication.

## Private setup

Set `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` and a distinct random `ADMIN_SESSION_SECRET` of at least 32 characters. There is no default password. Generate a PBKDF2 hash privately:

```powershell
python -c "import getpass; from src.routes.admin import make_password_hash; print(make_password_hash(getpass.getpass('Admin password: ')))"
```

The password is entered without echo and is not placed in shell history. Put only the returned `pbkdf2_sha256$...` value in the deployment environment. Do not commit either value. `ADMIN_COOKIE_SECURE=true` is mandatory behind Dokploy HTTPS; use false only for local HTTP testing.

Login creates a signed eight-hour HttpOnly, Secure, SameSite=Strict cookie scoped to `/admin`. Every mutation also requires the session CSRF token in `X-CSRF-Token`. Logout expires the cookie. Admin auth is separate from `X-Retell-Tool-Secret`; the dashboard never reveals that secret.

## Pages and actions

The single responsive dashboard shows today/upcoming/active/cancelled session counts and active rule count, followed by:

- Availability rules: create with canonical package ID or `*`, weekday, local start/end, effective dates and capacity; edit time/capacity; disable.
- Blackouts: create package/wildcard intervals in America/Chicago local time with optional note; view and disable. The backend converts them to UTC for storage. Full-day closure is represented by its exact start/end interval.
- Booking calendar/list: chronological sessions with customer, package, reference, start/end and status; search/filter; inspect group sessions/history; reschedule or cancel with confirmation.

Admin booking actions use the same internal provider transaction/capacity logic. Reschedule accepts explicit timezone-aware ISO timestamps, preserves session duration and fails if no configured slot exists. Cancellation releases capacity and returns `refund_issued:false`.

## Operating sequence

1. Log in and confirm the dashboard is empty on a fresh database.
2. Create an active rule with an explicit capacity. Use synthetic dates/data during QA.
3. Call the normal availability API and verify its slots match the rule.
4. Create through the normal API; confirm it immediately appears in bookings.
5. Add/disable a blackout and verify availability changes immediately.
6. Test reschedule/cancel and inspect history.
7. Restart the container with the same `/app/runtime` volume and confirm rules/bookings remain.

No manual booking creation, database download, arbitrary SQL, payment/refund action, resource assignment or analytics exists in this MVP.
