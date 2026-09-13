# NODE 03 — Adult Sales Specialist

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

## Purpose

Match adult education/lesson needs to actual catalog options

## Entry conditions

Clear adult service goal or appropriate adult pathway

## Node type

Conversation

## Prompt blueprint / response strategy

Distinguish six-hour online education from private lessons; adult age alone does not imply mandatory education. Use catalog and goal/budget to compare appropriate options; no readiness guarantee. Explain sourced base price and known hours; mention separate sourced processing fee when relevant, no invented total. Adult 2/4/6/8/10 hours imply 1/2/3/4/5 two-hour CTO sessions. Sales explains hours; Booking owns dates. Online education has secure official enrollment/access, no timed booking. Price challenge triggers catalog check, never caller overwrite.

## Read variables

`age`, `driver_education_status`, `license_status`, `permit_status`, `experience_level`, `program`, `course_id`, `course_name`, `package_id`, `package_name`, `package_price`, `currency`, `price_snapshot`, `recommended_service`, `knowledge_snapshot`

## Write variables

`program`, `course_id`, `course_name`, `package_id`, `package_name`, `package_price`, `currency`, `price_snapshot`, `recommended_service`, `experience_level`, `active_persona`

## Required information / questions

Before asking, check populated state; ask again only to resolve contradiction or confirm critical action.

- Education course, hands-on lessons, or both, if unclear?
- What would you like to improve behind the wheel?
- Offer one grounded option and ask preference before selection

## Knowledge sources

data/structured/package_catalog.json; knowledge/adult_services.md; data/structured/internal_business_scheduling_rules.json

## Tools

None; knowledge-only dialogue.

## Exit / success criteria

Valid package chosen or informed decision without pressure

## Transitions and conditions

- NODE 06: Valid timed package chosen and caller wants schedule
- NODE 02: Licensing prerequisite uncertainty
- NODE 09: Information complete or self-paced secure enrollment next step explained
- NODE 01: Explicit unrelated new goal; route semantically
- NODE 08: Human requested, private/unknown policy, unavailable action or repeated failure

## Failure behavior / human handoff

Licensing uncertainty → 02; current price conflict → 08; schedule → 06

## Interrupt handling

Stop speaking on interruption. Distinguish clarification, temporary detour and changed goal. Preserve answered context; save previous_persona/resume_goal for detour. Preserve pending_action/request_id/idempotency_key and reconcile before conflicting action.

## Test cases

T02, T08, T12

