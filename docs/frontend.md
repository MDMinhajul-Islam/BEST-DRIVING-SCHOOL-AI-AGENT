# Best Driving School website

The independent `frontend/` application uses Next.js 16 App Router, React 19,
TypeScript, Tailwind 4, Motion and Lucide. Versions are pinned in package.json
and package-lock.json. Node 20.9+ is required (validated with Node 24).

## Local website

```sh
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. The default is a visibly disabled voice demo; it
never simulates a call. The homepage, pricing previews, directions, phone links
and official course/enrollment links work independently of Python.

```sh
npm run lint
npm run typecheck
npm run build
npm start
```

## Voice configuration

The existing source had only `GET /api/health` and authenticated
`POST /api/booking/{operation}` (check-availability, create, find, reschedule,
cancel). It had no Retell web-call endpoint. Booking supports persistent mock
and guarded Cal.com demo/live modes. No booking route is exposed to this UI.

The new isolated app does not import or change booking or the knowledge pipeline:

Browser → Next `POST /api/voice/session` → FastAPI
`POST /api/retell/web-call` → Retell `POST /v2/create-web-call`.
Only temporary `access_token` and optional `call_id` return to the browser.
The browser uses RetellWebClient from retell-client-js-sdk, loaded on demand.
The installed 3.x SDK retains this documented legacy interface; pinning avoids
its planned removal in 4.x. See https://docs.retellai.com/deploy/web-call and
https://docs.retellai.com/api-references/create-web-call.

Create a Python 3.10+ environment and install the root requirements:

```sh
python3.14 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Supply these in the backend process environment (never public frontend variables):

- `RETELL_API_KEY`: private Retell API key.
- `RETELL_AGENT_ID`: your published, configured Best Driving School agent ID.
- `VOICE_PROXY_SECRET`: random secret of at least 32 characters.

```sh
.venv/bin/python -m uvicorn src.routes.voice:create_app --factory --host 127.0.0.1 --port 8001 --workers 1 --no-access-log
```

Set frontend `.env.local`:

```dotenv
NEXT_PUBLIC_VOICE_DEMO_MODE=false
VOICE_BACKEND_URL=http://127.0.0.1:8001
VOICE_PROXY_SECRET=the-same-server-only-secret
SITE_ORIGIN=http://localhost:3000
```

Restart Next after changes; rebuild for public build-time environment changes.
Use the exact public HTTPS origin for `SITE_ORIGIN` in production (no trailing
slash). It controls the Origin check and metadata base. The broker must remain
on a private network behind Next; no CORS wildcard is needed. Missing config
fails closed. Responses are no-store; no tokens are persisted or logged by
application code. Retell's agent controls recording/data retention: review those
settings and the school's privacy policy before enabling calls.

The broker caps creation at 10 attempts per minute per process. Use one worker;
add shared edge rate limiting/bot protection and Retell spending limits before
public launch. Origin validation is a browser cross-site protection, not bot
authentication. Scale with a shared limiter, not additional independent workers.

A single provider owns the SDK, cancellation guard, timers and microphone. Modal
closing and anchor navigation preserve a call. Only the SDK call_started event
marks a connection. Duplicate clicks are locked synchronously. Cancellation
invalidates late async results. Microphone metering uses a local audio analyser;
muting disables both the meter's track and the SDK microphone. Cleanup stops
tracks, SDK audio, listeners, intervals and requests. No fake transcript is used.

HTTPS is required for deployed microphone access. Test Safari/iOS using a real
HTTPS origin and headphones; browser/autoplay policy and real Retell audio cannot
be certified by offline mocks. No credentials, agent creation, paid calls or
Retell dashboard changes were performed for this implementation.

## Existing Python functionality

The knowledge pipeline still runs with `.venv/bin/python -m src.main --offline`.
See the root README for scraping, regulatory review and full pipeline commands.
The separate booking backend retains its existing run command:

```sh
.venv/bin/python -m uvicorn src.routes.booking:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

It requires the existing `RETELL_TOOL_SECRET` and booking environment configuration.
`BOOKING_MODE=mock` remains synthetic; this website never presents its data as
availability. No new booking, payment, calendar, account or enrollment API was
implemented. Course links use the existing school workflow.

## Content and design

`lib/content/school.ts` centralizes contact, hours, testimonials and trust facts
from the saved homepage/business overview. `lib/content/programs.ts` is a small
typed projection of `data/structured/package_catalog.json`, using only
`price_status=verified_saved_snapshot` amounts. Refresh these projections after
reviewing a new knowledge snapshot. Dates and processing fees are visible beside
prices; prices are not live quotes. Ratings and quotations are attributed to the
school website snapshot. No aggregate rating is put in structured data.

Licensing approval, teen regulatory hour requirements, pass-rate and unverified
eligibility claims are omitted. The school logo is stored locally unchanged,
from https://bestdrivingschool.us/redesign/img/logo-primary.webp.

A decorative SVG road and CSS orb create depth without WebGL or a large 3D
runtime. Animations honor reduced motion; the page stays mostly server rendered.
The dialog uses native focus trapping/Escape behavior; floating call controls
appear after the hero exits. The schematic location graphic is explicitly not a
navigation map; directions use the official saved external link.

## Validation

`tests/test_voice.py` verifies authentication, disabled configuration, token
allowlisting, sanitization, malformed responses and rate limiting without
contacting Retell. Run `.venv/bin/python -m unittest discover -s tests -v`.
The existing suite has three preservation-hash failures in untouched files:
`knowledge/regulatory/adult_first_time_license.md` (two checks) and
`docs/retell_manual_build_spec.md` (one). The new endpoint tests pass.

Browser verification completed at 390px, 768px and 1440px. The primary mobile
call control fits in an 844px viewport. Playwright covers the disabled demo,
mobile navigation, native dialog focus/return, cross-origin rejection, microphone
denial, unsupported browsers, network/service failures, late-track cancellation
and timeout. Axe reports no WCAG 2 A/AA or 2.1 AA violations in the homepage and
dialog scans. This is automated coverage, not a complete accessibility certification.

To repeat the standard browser checks, start the default demo site, install
Playwright Chromium (`npx playwright install chromium`), then run `npm test` in
`frontend/`. `TEST_BASE_URL` can point to another local port. Optionally set
`PLAYWRIGHT_EXECUTABLE_PATH` to a locally installed Chromium-family browser.

For the error-path tests, run a separate development server:

```sh
NEXT_PUBLIC_VOICE_DEMO_MODE=false npm run dev -- --port 3003
```

Then in another terminal:

```sh
TEST_BASE_URL=http://localhost:3003 TEST_LIVE_PATH=1 npm test -- voice-errors
```

These tests replace media capture and intercept session HTTP calls. They do not
contact Retell or transmit microphone audio. Actual connected/speaking/mute/end
behavior and Safari/iOS playback still need an end-to-end call with configured
Retell credentials. No private environment variable names were found in the
production client chunks during the final bundle check.
