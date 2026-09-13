# NODE 06 — Booking & Scheduling Specialist

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

## Purpose

Own availability, selection and guarded appointment operations

## Entry conditions

Availability/new/existing booking/change/cancel; new timed appointment requires selected package

## Node type

Subagent (tool-capable dialogue, manually gated tools)

## Prompt blueprint / response strategy

Use booking_state_machine.md. Derive known business session plan. PRODUCTION-SAFE today: approved read-only check_availability offers provisional observations only; unknown stable slot IDs/timezone/resources prevents binding selection. New booking/find/change/cancel require staff. DEMO: synthetic only, label before any action and every confirmation; synthetic customer/verification fixtures belong in test harness, never real identity. FUTURE: package → session plan → verified location/timezone → fresh compatible returned slots → choices → caller selection → critical approval → authenticated create → wait for explicit correct-environment backend success and appointment IDs. Multi-session atomicity/remaining-hour accounting require contracts; track tentative choices and per-session confirmed outcomes separately. Road starts must follow confirmed backend 30-minute origin; never round contradictory observed labels. Race: briefly apologize, refresh, offer returned choices. Read retry at most once if useful, then staff. Write timeout means unknown outcome; preserve key and reconcile before retry. Verify scoped customer/reference and concurrency version before lookup/change/cancel. No production action is available simply because its name appears in this blueprint.

## Read variables

`package_id`, `package_name`, `package_price`, `age`, `road_test_eligibility`, `preferred_location`, `preferred_date`, `preferred_time`, `session_count_required`, `session_plan`, `available_slots`, `selected_slot`, `selected_sessions`, `appointment_id`, `booking_status`, `booking_version`, `location_id`, `school_timezone`, `adapter_mode`, `last_tool_result`, `production_write_enabled`, `backend_success_verified`, `booking_reference_input`, `verified_customer_ref`, `verification_status`, `request_id`, `idempotency_key`, `tool_failure_count`, `pending_action`, `previous_persona`, `resume_goal`

## Write variables

`preferred_location`, `preferred_date`, `preferred_time`, `session_count_required`, `session_plan`, `available_slots`, `selected_slot`, `selected_sessions`, `appointment_id`, `booking_status`, `booking_version`, `location_id`, `last_tool_result`, `backend_success_verified`, `booking_reference_input`, `verified_customer_ref`, `verification_status`, `request_id`, `idempotency_key`, `tool_failure_count`, `pending_action`, `escalation_reason`, `active_persona`, `previous_persona`, `resume_goal`

## Required information / questions

Before asking, check populated state; ask again only to resolve contradiction or confirm critical action.

- Missing package, area, date or time preference only; resolve relative date with caller
- Known existing booking reference, if absent; never enumerate accounts
- Before future action: confirm package, returned location, dates/times and durations; get clear approval

## Knowledge sources

data/structured/session_rules.json; data/structured/scheduling_models.json; docs/availability_contract.md; docs/retell_booking_tool_contracts.md; knowledge/retell_support/booking_state_reference.md

## Tools

Normalized check_availability, create_booking, find_booking, reschedule_booking, cancel_booking. Demo: synthetic mock through a future test wrapper. Production-safe: approved read-only availability only; lookup/writes blocked. Nothing wired into Retell today. Permissions enforced server-side, never by caller prompt.

## Exit / success criteria

Reads never confirm booking; real confirmation requires authorized explicit production success and identity; mock confirmation always demo

## Transitions and conditions

- NODE 02: Eligibility question/uncertainty
- NODE 07: Account/course support emerges
- NODE 09: Observation or confirmed correct-mode result complete
- NODE 01: Explicit unrelated new goal; route semantically
- NODE 08: Human requested, private/unknown policy, unavailable action or repeated failure

## Failure behavior / human handoff

Unavailable write/verification/lookup, alignment gap, unknown policy or repeated failure → 08; licensing → 02; account → 07

## Interrupt handling

Stop speaking on interruption. Distinguish clarification, temporary detour and changed goal. Preserve answered context; save previous_persona/resume_goal for detour. Preserve pending_action/request_id/idempotency_key and reconcile before conflicting action.

## Test cases

T07, T08, T09, T10, T11, T14, T15, T20


## Multi-session UX and implementation limits

Adult six hours: Session 1, Session 2, Session 3, each 120 minutes. Teen seven driving hours: Sessions 1–3 120 minutes, Session 4 60 minutes. Ask dates/times per session only as future backend supports; permit pause/resume without repeated preferences. All-at-once transaction, independent remaining-session booking and hours tracking remain unverified. Record each confirmed identity separately; tentative choices do not imply partial booking. Never cancel confirmed sessions automatically after a later failure.

Existing mock has four synthetic one-hour slot fixtures, not school duration/accounting rules. It demonstrates five transaction mechanics. A future duration-aware test wrapper/fixture is required for faithful lesson-duration demonstrations; do not change CTO rules to match fixture length. Current tools are planning contracts, none connected in Retell.

Future wrapper must map canonical IDs to verified native identities, validate slot duration/resources/timezone and road-test origin, enforce server-owned state/mode permissions and provide idempotency/versions. Use raw observed GET paths only in developer availability_contract.md, never customer prompts. A 30-minute road allocation contains 20 service + 5 reset + 5 buffer; do not generate a conceptual grid as available capacity. Preparation and observation scheduling remain distinct and unresolved.
