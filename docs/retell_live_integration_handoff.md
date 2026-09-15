# Best Driving School — Retell live integration handoff

Audited September 15, 2026. This is the definitive manual wiring specification for the deployed internal booking system. It does not authorize or record any Retell change. Secret values are intentionally omitted. Cal.com is disabled and irrelevant to this phase.

## Deployment evidence

| Surface | URL | Audit result |
|---|---|---|
| Backend | `https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io` | HTTPS reachable |
| Health | `https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io/api/health` | HTTP 200; `provider: internal`; `timezone: America/Chicago` |
| Admin | `https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io/admin` | HTTP 200 login shell; data API requires separate admin login |
| Frontend | `https://minhaj-bds-frontend-7wmdcd-5ad051-206-189-183-167.sslip.io` | HTTPS HTTP 200; Next.js |

The HTTPS checks used normal certificate validation. The health response was exactly:

```json
{"status":"ok","service":"best-driving-school-booking-api","provider":"internal","timezone":"America/Chicago"}
```

The root backend path has no route and may correctly return `{"detail":"Not Found"}`. Health is the readiness endpoint.

## Authentication and transport

All five tools use `POST`, `Content-Type: application/json`, and these headers:

```text
X-Retell-Tool-Secret: <exact value stored in RETELL_TOOL_SECRET>
X-Booking-Scope: <trusted stable scope, 16–128 characters matching [A-Za-z0-9_-]>
```

`X-Retell-Tool-Secret` is a raw static header value. There is **no** `Bearer` prefix. The same private value configured as `RETELL_TOOL_SECRET` in Dokploy must later be entered as the static Retell header value. It must never become a dynamic variable, prompt value, frontend variable, or spoken value.

For Retell Custom Functions, enable **Payload: args only** so the body is the flat parameter object shown below. The backend also accepts Retell's normal `{name, call, args}` envelope, discards call metadata, and validates only `args`. Retell supports static/dynamic headers and `{{call_id}}` as a built-in dynamic variable; use its variable picker rather than typing an unrecognized placeholder.

### Scope rule and cross-call limitation

Within one call, set `X-Booking-Scope: {{call_id}}` on every tool. This isolates callers and keeps availability refs, booking refs and writes in one trusted scope.

An appointment can only be found, rescheduled or cancelled using the scope that created it. A later call has a different `call_id`. Cross-call existing-booking operations are therefore **blocked unless a stable, trusted customer scope is injected server-side at call creation/inbound routing and reused**. Do not ask a caller to supply a scope and do not weaken this check. Same-call create/find/reschedule/cancel is ready.

Requests are limited to 64 KiB. Unknown body fields are rejected. Missing/invalid secret or scope returns HTTP 401. Domain failures normally return HTTP 200 with `success:false`; transport/schema errors can return 400/413, unknown operations 404, and unexpected infrastructure failures 503.

## Common response semantics

Successful responses include:

```json
{
  "success": true,
  "mode": "internal",
  "booking_provider": "internal",
  "production": false,
  "synthetic": false,
  "demo": true,
  "booking_confirmed": false
}
```

Operation fields are added to this base. The `production:false` and `demo:true` labels are current API fields; runtime storage/provider is nevertheless the deployed internal system. Never use either field alone to infer booking success.

Domain failures have this exact shape:

```json
{
  "success": false,
  "mode": "internal",
  "booking_provider": "internal",
  "production": false,
  "demo": true,
  "booking_confirmed": false,
  "error_code": "SLOT_UNAVAILABLE",
  "user_safe_message": "That time is no longer available. Please check other times."
}
```

Relevant error codes are `AUTHENTICATION_FAILURE`, `VALIDATION_ERROR`, `INVALID_PACKAGE`, `PACKAGE_REQUIRES_REVIEW`, `NOT_SCHEDULABLE`, `UNSUPPORTED_DURATION`, `CUSTOMER_DATA_MISSING`, `SLOT_UNAVAILABLE`, `BOOKING_NOT_FOUND`, `OUTCOME_UNKNOWN`, `PARTIAL_BOOKING`, and `PROVIDER_UNAVAILABLE`. The internal atomic create path does not intentionally produce partial groups, but callers must still fail closed on missing/partial fields.

## Tool 1 — check_availability

**Recommended description:** Check the internal calendar for one known canonical service and one customer-requested America/Chicago date. Offer only returned slots. Never infer availability. This tool does not create or confirm a booking.

- Method/URL: `POST https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io/api/booking/check-availability`
- Authentication: both common headers
- When to call: after a schedulable canonical service and date are known; call again after a conflict or for an alternate date.
- When not to call: for blocked/self-paced services, an unknown service, or before the caller gives a date.

Retell parameter schema:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["package_id", "preferred_date"],
  "properties": {
    "package_id": {"type": "string", "description": "Exact canonical schedulable service ID."},
    "preferred_date": {"type": "string", "description": "One America/Chicago calendar date in YYYY-MM-DD format."},
    "session_duration_minutes": {"type": "integer", "enum": [30, 60, 120], "description": "Omit normally; when used, it must occur in the selected package plan."},
    "preferred_time_window": {"type": "string", "enum": ["morning", "afternoon", "evening"]},
    "timezone": {"type": "string", "const": "America/Chicago"}
  }
}
```

There is no date-range or location field. Multi-session packages return slots for one requested plan duration; Retell must collect the exact number and duration sequence before create. Capacity and blackouts are already applied. Slot refs are opaque, scope-bound and expire after five minutes.

Synthetic request:

```json
{"package_id":"adult_4_hours","preferred_date":"2030-10-07","timezone":"America/Chicago"}
```

Synthetic success example:

```json
{
  "success":true,"mode":"internal","booking_provider":"internal","production":false,"synthetic":false,"demo":true,"booking_confirmed":false,
  "package_id":"adult_4_hours","timezone":"America/Chicago","scheduling_required":true,
  "session_plan":[120,120],"session_count_required":2,
  "available_slots":[{"slot_ref":"synthetic-scope-bound-ref-1","slot_id":"synthetic-scope-bound-ref-1","start":"2030-10-07T14:00:00Z","end":"2030-10-07T16:00:00Z","duration_minutes":120,"timezone":"America/Chicago"}],
  "slots":[{"slot_ref":"synthetic-scope-bound-ref-1","slot_id":"synthetic-scope-bound-ref-1","start":"2030-10-07T14:00:00Z","end":"2030-10-07T16:00:00Z","duration_minutes":120,"timezone":"America/Chicago"}]
}
```

Synthetic empty-availability response:

```json
{
  "success":true,"mode":"internal","booking_provider":"internal","production":false,"synthetic":false,"demo":true,"booking_confirmed":false,
  "package_id":"adult_4_hours","timezone":"America/Chicago","scheduling_required":true,
  "session_plan":[120,120],"session_count_required":2,"available_slots":[],"slots":[]
}
```

This is a successful check, not a booking. An unsupported duration returns:

```json
{"success":false,"mode":"internal","booking_provider":"internal","production":false,"demo":true,"booking_confirmed":false,"error_code":"UNSUPPORTED_DURATION","user_safe_message":"The scheduling request could not be completed safely."}
```

## Tool 2 — create_booking

**Recommended description:** Atomically create every required session for a selected canonical package using fresh slot refs returned under this same call scope. Call only after the caller confirms the exact slots, name and email. Confirm only from the strict success condition below.

- Method/URL: `POST https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io/api/booking/create`
- Required fields: `package_id` string; `slot_ids` array of unique strings in exact plan order; `customer` object containing exactly `name` and `email`.
- Customer validation: trimmed non-empty name up to 100 characters; syntactically valid email up to 254 characters.
- No phone, DOB, address, permit/license/document number, payment/card data, verification token, location, price, or refund data is accepted.
- Timestamps/timezone are not submitted to create; selected opaque refs carry them.
- Single-session and atomic multi-session booking are supported.

Exact multi-session counts:

| Package | Required `slot_ids` duration order |
|---|---|
| `adult_4_hours` | `[120, 120]` |
| `adult_6_hours` | `[120, 120, 120]` |
| Teen seven driving hours | `[120, 120, 120, 60]` |

Observation hours are not included or scheduled.

Retell parameter schema:

```json
{
  "type":"object","additionalProperties":false,
  "required":["package_id","slot_ids","customer"],
  "properties":{
    "package_id":{"type":"string"},
    "slot_ids":{"type":"array","minItems":1,"uniqueItems":true,"items":{"type":"string"}},
    "customer":{"type":"object","additionalProperties":false,"required":["name","email"],"properties":{"name":{"type":"string"},"email":{"type":"string"}}}
  }
}
```

Synthetic request:

```json
{"package_id":"adult_4_hours","slot_ids":["synthetic-ref-a","synthetic-ref-b"],"customer":{"name":"Test Student","email":"test.student@example.invalid"}}
```

Synthetic confirmed response:

```json
{
  "success":true,"mode":"internal","booking_provider":"internal","production":false,"synthetic":false,"demo":true,
  "booking_confirmed":true,"package_id":"adult_4_hours","booking_group_id":"IG-synthetic-group",
  "package_booking_status":"confirmed",
  "sessions":[
    {"index":1,"appointment_id":"INTERNAL-synthetic-appointment-1","start":"2030-10-07T14:00:00Z","end":"2030-10-07T16:00:00Z","booking_status":"confirmed"},
    {"index":2,"appointment_id":"INTERNAL-synthetic-appointment-2","start":"2030-10-08T14:00:00Z","end":"2030-10-08T16:00:00Z","booking_status":"confirmed"}
  ]
}
```

The caller-facing reference for each appointment is `sessions[].appointment_id`. Store and read it back as `booking_reference`. `booking_group_id` is an internal group reference useful for staff context; current reschedule/cancel tools operate on individual `appointment_id`, not the group.

Strict create success is: `success == true`, `booking_confirmed == true`, `package_booking_status == "confirmed"`, session count equals the plan, and every session has `booking_status == "confirmed"` plus a non-empty `appointment_id`. Anything else is failure/uncertain and must not be spoken as confirmed.

## Tool 3 — find_booking

**Recommended description:** Find one known appointment reference within the current trusted booking scope. Never search by name, email or phone and never enumerate bookings.

- Method/URL: `POST https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io/api/booking/find`
- Body schema: `{"type":"object","additionalProperties":false,"required":["appointment_id"],"properties":{"appointment_id":{"type":"string"}}}`
- Customer verification fields: none. Privacy is enforced by opaque reference plus trusted scope; do not claim this authenticates a caller across calls.
- Safe returned data: reference, UTC start/end, status and confirmation boolean. No customer contact/provider UID is returned.

Confirmed example:

```json
{"success":true,"mode":"internal","booking_provider":"internal","production":false,"synthetic":false,"demo":true,"booking_confirmed":true,"appointment_id":"INTERNAL-synthetic-appointment-1","start":"2030-10-07T14:00:00Z","end":"2030-10-07T16:00:00Z","booking_status":"confirmed"}
```

Not found is HTTP 200 with `success:false`, `booking_confirmed:false`, `error_code:"BOOKING_NOT_FOUND"`. Clarify the appointment reference once; then escalate. Cross-call lookup remains blocked without the original trusted scope.

## Tool 4 — reschedule_booking

**Recommended description:** Move one known individual appointment to one fresh same-duration slot returned by check_availability under the same trusted scope. Revalidation and conflict protection occur atomically.

- Method/URL: `POST https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io/api/booking/reschedule`
- Body schema: `{"type":"object","additionalProperties":false,"required":["appointment_id","slot_ref"],"properties":{"appointment_id":{"type":"string"},"slot_ref":{"type":"string"}}}`
- Target: one session, not a booking group.
- Replacement: opaque, fresh `slot_ref`; never a caller-invented timestamp.
- Backend: requires accepted session, preserves duration, revalidates active rule/blackout/capacity, excludes the current session from its conflict count, updates atomically and records history.

Synthetic request:

```json
{"appointment_id":"INTERNAL-synthetic-appointment-1","slot_ref":"synthetic-fresh-slot-ref"}
```

Success uses the find shape with the new UTC times and requires `success == true && booking_confirmed == true && booking_status == "confirmed"`. `SLOT_UNAVAILABLE` means conflict: do not retry the stale ref; run check_availability again and ask the caller to choose.

## Tool 5 — cancel_booking

**Recommended description:** Cancel one known individual appointment reference in the same trusted scope after the caller explicitly confirms cancellation. This does not issue or promise a refund.

- Method/URL: `POST https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io/api/booking/cancel`
- Body schema: `{"type":"object","additionalProperties":false,"required":["appointment_id"],"properties":{"appointment_id":{"type":"string"}}}`
- Target: one session. Cancel every desired group session separately with explicit caller intent.
- Backend behavior: accepted becomes cancelled, history is recorded, capacity is released, and the group becomes cancelled when no accepted sessions remain. Repeating the identical request returns current cancelled state.

Synthetic request/response:

```json
{"appointment_id":"INTERNAL-synthetic-appointment-1"}
```

```json
{"success":true,"mode":"internal","booking_provider":"internal","production":false,"synthetic":false,"demo":true,"booking_confirmed":false,"appointment_id":"INTERNAL-synthetic-appointment-1","start":"2030-10-07T14:00:00Z","end":"2030-10-07T16:00:00Z","booking_status":"cancelled","refund_issued":false}
```

Cancellation success is `success == true && booking_status == "cancelled" && refund_issued == false`. `booking_confirmed` is correctly false after cancellation. Never say a refund was requested, approved or issued.

## Idempotency and retries

There is no `Idempotency-Key` header or client idempotency field. The backend derives a durable SHA-256 action key from the exact normalized tuple `(X-Booking-Scope, mode, operation, payload)` for create, reschedule and cancel. Identical scope + operation + body reuses the recorded result after restart and prevents duplicate creation. A changed body is a different action.

- `check_availability`: read-only; no write idempotency record.
- `create_booking`, `reschedule_booking`, `cancel_booking`: derived idempotency supported automatically.
- Safe retry: only repeat the exact same body and exact same scope when the previous response is known and a transport retry is necessary.
- `OUTCOME_UNKNOWN`, timeout, 5xx or ambiguous/missing response: do not automatically issue a changed or second write; escalate/reconcile.
- A slot ref expires after five minutes; refresh availability instead of retrying an expired/conflicted selection.

## Service/package matrix

These are canonical internal IDs, not observed website backend product IDs.

| Internal ID | Customer-facing name | Category | Schedulable | Session plan minutes | Auto |
|---|---|---|---|---|---|
| `teen_24_hr_classroom_driving_package` | 24 Hr Classroom + Driving Package | Teen | Yes, driving portion only | `[120,120,120,60]` | Yes |
| `teen_behind_the_wheel_only_7_7` | Behind the Wheel Only (7 & 7) | Teen | Yes, driving portion only | `[120,120,120,60]` | Yes |
| `adult_2_hours` | 2 hours | Adult driving | Yes | `[120]` | Yes |
| `adult_4_hours` | 4 hours | Adult driving | Yes | `[120,120]` | Yes |
| `adult_6_hours` | 6 hours | Adult driving | Yes | `[120,120,120]` | Yes |
| `adult_8_hours` | 8 hours | Adult driving | Yes | `[120,120,120,120]` | Yes |
| `adult_10_hours` | 10 hours | Adult driving | Yes | `[120,120,120,120,120]` | Yes |
| `road_test_road_test_only` | Road test only | Road test | Yes | `[30]` | Yes |
| `parent_taught_10_hours` | 10 hours | Parent taught/PTDE | No | unresolved | No |
| `parent_taught_15_hours` | 15 hours | Parent taught/PTDE | No | unresolved | No |
| `parent_taught_30_hours` | 30 hours | Parent taught/PTDE | No | unresolved | No |
| `adult_6_hour_online_permit_class` | 6-Hour Online Permit Class | Online/self-paced | No timed appointment | `[]` conceptually | No |
| `road_test_practice_session_road_test` | Practice session + road test | Road test | No | duration/allocation unresolved | No |

Blocked PTDE and Practice + Road Test requests go to Human Escalation. The online course is information/enrollment guidance only and returns `NOT_SCHEDULABLE`; do not create a calendar appointment. Teen observation hours are separate and must not be added to `slot_ids`; observation scheduling needs staff handling. Even an auto-schedulable service returns no slots until an admin creates an explicit positive-capacity rule.

## Live calendar status and location model

The authenticated deployed booking API returned HTTP 200 and zero slots for every auto-schedulable ID across September 15–21, 2026. Therefore the audited caller-visible status is:

**NO LIVE AVAILABILITY CONFIGURED for the audited week.**

The protected admin rule/capacity/blackout tables cannot be enumerated through any public endpoint, by design. Exact stored rule and blackout counts require an authenticated admin session; no credentials were exposed or bypassed during this audit. Retell wiring may be prepared, but end-to-end booking cannot pass until an authorized admin adds real rules with positive capacity. No business hours were inferred.

The public booking contract has **no location parameter and no location ID**. It models no branch/resource selection. Plano is the verified office/testing location in the knowledge base; Allen, Frisco and McKinney remain advertised service areas. Do not invent or pass branch IDs.

## Timezone rules

`preferred_date` is a local America/Chicago calendar date (`YYYY-MM-DD`). Optional `timezone`, when sent, must equal `America/Chicago`. Availability responses return `start` and `end` as UTC ISO-8601 timestamps ending in `Z`. Create/reschedule use opaque slot refs rather than caller-supplied times.

Example: `2030-10-07T14:00:00Z` corresponds to a Chicago-local time according to the DST offset on that date. Retell should read the returned timestamp to the caller in America/Chicago and retain the exact ref. It must never add a fixed offset or calculate a slot from business hours.

## Machine result interpretation

| Class | Exact condition/action |
|---|---|
| Availability success | `success == true`; slots may be empty; never treat as booking confirmation |
| Create success | strict multi-field/session condition defined above |
| Find/reschedule success | `success == true && booking_confirmed == true && booking_status == "confirmed"` |
| Cancel success | `success == true && booking_status == "cancelled" && refund_issued == false` |
| Failure | `success != true`, missing required success fields, partial/mismatched sessions or unexpected status |
| Conflict | `error_code == "SLOT_UNAVAILABLE"`; refresh availability |
| Not found | `error_code == "BOOKING_NOT_FOUND"`; clarify once, then escalate |
| Unauthorized | HTTP 401 and `error_code == "AUTHENTICATION_FAILURE"`; never ask caller for the secret |
| Validation | HTTP 400 or domain response with validation/package/duration/customer error; correct known inputs or escalate |
| Provider/server | HTTP 503, `PROVIDER_UNAVAILABLE`, `OUTCOME_UNKNOWN`, timeout or non-JSON; do not confirm/retry uncertain writes |

## Minimal shared Retell variables

Retell dynamic variables are strings. Keep existing `student_age` in its current tested configuration and add only:

| Variable | Type | Populate | Purpose |
|---|---|---|---|
| `selected_service_id` | string | after exact package selection | Canonical `package_id` for availability/create |
| `preferred_date` | string | after caller gives local date | `YYYY-MM-DD` availability input |
| `customer_name` | string | immediately before create | Required customer field |
| `customer_email` | string | immediately before create | Required customer field |
| `booking_reference` | string | from confirmed `appointment_id` | find/reschedule/cancel and spoken reference |
| `booking_status` | string | from confirmed tool result | guarded confirmation/cancellation state |

`preferred_time` can remain conversational until a returned slot is selected; the tool needs the returned `slot_ref`, not a free-form time. `selected_slot_refs` is useful only as temporary subagent state for multi-session create and should not be spoken or retained after the action. `selected_package_name` is presentation-only and unnecessary for the API. `customer_phone` is not accepted by the API. Do not collect DOB, address, permit/license/document numbers, passwords, authentication tokens, payment/card data or refund details for these tools.

## Booking Subagent wiring

Attach all five Custom Function tools directly to **Booking & Scheduling Specialist — SUBAGENT**. No additional Function Node or Code Node is needed. No Logic Split is required merely to parse these structured results if the subagent prompt contains the exact guards and transitions below. Response-variable extraction is recommended for confirmed `appointment_id → booking_reference` and `booking_status`; do not extract an ID from a failed result.

Recommended transitions/behavior:

- Availability found: offer only returned slots and remain in Booking Subagent.
- Empty availability: ask for another date and call again.
- Slot conflict: refresh availability; never reuse the stale ref.
- Create strict success: confirm every session and state each appointment reference.
- Create uncertain/error/partial: do not confirm; Human Escalation when reconciliation or repeated failure is needed.
- Booking not found: clarify reference once; Human Escalation if unresolved or cross-call scope is unavailable.
- Reschedule success: confirm the returned new America/Chicago appointment time.
- Cancel success: confirm cancellation and explicitly avoid any refund claim.
- Auth/503/non-JSON/timeout: Human Escalation; do not expose or ask for credentials.

A Logic Split may be added later for deterministic analytics, but it is optional and would duplicate conditions the tool-aware subagent can apply. Keep the existing flow architecture.

## Human escalation and admin relationship

Verified public contact: **+1-469-709-7613**, sourced from `knowledge/retell_kb_ready/human_escalation/verified_contact.md` and the canonical `data/structured/locations.json`, ultimately backed by the public Plano location page. It is presented publicly as Best Driving School's call/text contact and is appropriate as the candidate customer-support transfer destination. Staff availability and transfer-answer behavior are not verified, so configure transfer fallback and never promise a live answer.

Internal API bookings insert the booking group, every session, generic reference mapping and history in one transaction. They appear in the authenticated Admin Dashboard, consume capacity, are searchable by admin, can be individually rescheduled/cancelled by admin using the same calendar safeguards, and persist in `/app/runtime/booking.sqlite3` across restart when the Dokploy volume is mounted. This relationship is covered by automated and container persistence tests.

## Security audit

- PASS: live HTTPS and certificate validation on frontend/backend/admin.
- PASS: booking routes require secret plus trusted scope; unauthenticated requests return 401.
- PASS: health exposes only service/provider/timezone.
- PASS: admin uses separate PBKDF2 login, signed HttpOnly/Secure/SameSite cookie and CSRF on writes.
- PASS: no booking/admin secret is referenced by frontend source or public frontend environment.
- PASS: there is no public database download, arbitrary SQL or OpenAPI/docs endpoint.
- PASS: server-to-server security relies on authentication, not CORS.
- PASS: deployed provider is internal; no Cal.com setup is required.
- BLOCKER: cross-call existing-booking operations need a trusted stable scope injected into Retell; `{{call_id}}` covers only one call.
- BLOCKER: no slots were returned in the audited week; admin must configure approved hours/capacity before an end-to-end booking test.

## Final Retell work checklist

| Status | Work |
|---|---|
| DONE | Conversation Flow, specialist prompts, knowledge bases, age extraction, Adult/Teen Logic Split |
| DONE | Deployed internal backend/frontend, HTTPS health, admin surface, five-operation implementation |
| REMAINING | Create five Custom Function tools with args-only payload and exact headers/schemas |
| REMAINING | Put the existing Dokploy secret into each tool's static `X-Retell-Tool-Secret` header |
| REMAINING | Use `{{call_id}}` for same-call `X-Booking-Scope`; decide/inject a trusted stable scope before enabling cross-call support |
| REMAINING | Attach all five tools only to Booking & Scheduling Specialist |
| REMAINING | Add minimal variables and strict result-handling instructions/extractions |
| REMAINING | Authorized admin enters verified availability/capacity; test blackout behavior |
| REMAINING | Test empty slots, single adult, multi-session adult, teen 120/120/120/60, road test, conflict, same-call find/reschedule/cancel, auth failure, timeout and escalation |
| REMAINING | Configure/test transfer to `+1-469-709-7613` with failure fallback if call transfer is part of the demo |
| OPTIONAL | Post-call extraction of selected service, booking reference/status, escalation reason and outcome; avoid unnecessary PII |
| OPTIONAL | Logic Splits after tools; structured subagent handling is sufficient for the MVP |
| BLOCKED | Cross-call find/reschedule/cancel until trusted stable scope delivery is defined |
| BLOCKED | End-to-end create until admin-configured live availability exists |
| REMAINING | Review unpublished draft, run test matrix, then publish manually |

The exact next Retell step is: create the `check_availability` Custom Function in draft with args-only payload, static `X-Retell-Tool-Secret`, dynamic `X-Booking-Scope: {{call_id}}`, the schema above, and do not publish yet.

## References

- Local API contract: `docs/retell_booking_api_contract.md`
- Internal model: `docs/internal_calendar_architecture.md`
- Admin operation: `docs/admin_dashboard_guide.md`
- Retell Custom Function documentation: <https://docs.retellai.com/build/conversation-flow/custom-function>
- Retell dynamic variables: <https://docs.retellai.com/build/dynamic-variables>
