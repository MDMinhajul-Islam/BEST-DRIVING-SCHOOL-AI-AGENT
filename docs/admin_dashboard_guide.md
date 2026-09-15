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

The responsive dashboard uses five focused sections: Overview, Availability, Blackouts, Bookings and System. Overview shows today/upcoming/active/cancelled session counts, active rule and blackout counts, and upcoming sessions. All displayed counts and rows come from the internal SQLite calendar.

- Availability rules: select one of the eight canonical schedulable services (or all services), see its required session plan, create a weekday window with explicit effective dates/capacity, edit its time/capacity, and activate or disable it. Windows shorter than the service's minimum session length are rejected.
- Blackouts: create a service-specific or all-service interval in America/Chicago local time with an optional note, then activate or disable it. The backend converts local values to UTC for storage.
- Bookings: search/filter chronological sessions, inspect a structured booking/group/history view, reschedule in America/Chicago local time, or cancel after confirmation. Session index and booking group context stay visible for multi-session packages.
- System: confirms the active provider, timezone and health endpoint without exposing credentials.

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

## Controlled Retell availability test

Use this synthetic, far-future rule so the test is deterministic and unlikely to affect normal operations. Do not create it automatically; a signed-in staff member controls the write.

1. In **Availability**, choose `Adult 2 Hours` (`adult_2_hours`).
2. Set weekday to **Monday**, start to **09:00**, end to **11:00**, effective start and end to **2035-10-01**, and capacity to **1**. Times are America/Chicago.
3. Save the rule and confirm it appears as Active.
4. In Retell, ask for Adult 2 Hours availability on October 1, 2035. The expected single slot starts at 9:00 AM America/Chicago (14:00 UTC).
5. Complete the create/find/reschedule/cancel checks using clearly synthetic customer details. Respect the current call-scope rule for every lookup or mutation.
6. Return to Availability and disable the rule immediately after testing. Confirm a second availability check returns no slots for that controlled window.
