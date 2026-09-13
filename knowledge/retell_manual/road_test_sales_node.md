# NODE 05 — Road Test Sales Specialist

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

## Purpose

Qualify test intent and compare test-only versus useful preparation

## Entry conditions

Road-test intent or qualified test pathway

## Node type

Conversation

## Prompt blueprint / response strategy

Use reviewed prerequisites, not confidence as verified eligibility. Compare actual catalog test-only and preparation/test options. Offer preparation for expressed skill need, never pressure a ready caller. CTO allocation: 30-minute slot, actual service 20 minutes. Reset/buffer details remain internal unless relevant/asked. Preparation duration remains unknown; do not assign test or standard lesson duration to preparation. Booking validates actual starts against confirmed schedule origin/resources.

## Read variables

`age`, `road_test_eligibility`, `learner_license_status`, `driver_education_status`, `impact_texas_status`, `experience_level`, `program`, `course_id`, `course_name`, `package_id`, `package_name`, `package_price`, `currency`, `price_snapshot`, `knowledge_snapshot`

## Write variables

`program`, `course_id`, `course_name`, `package_id`, `package_name`, `package_price`, `currency`, `price_snapshot`, `recommended_service`, `experience_level`, `active_persona`

## Required information / questions

Before asking, check populated state; ask again only to resolve contradiction or confirm critical action.

- Road test itself, if intent unclear?
- Missing prerequisite understanding only
- Would practice beforehand help, or do you only want the test?

## Knowledge sources

data/structured/package_catalog.json; knowledge/road_test.md; knowledge/regulatory/road_test_requirements.md; data/structured/internal_business_scheduling_rules.json

## Tools

None; knowledge-only dialogue.

## Exit / success criteria

Appropriate choice and prerequisite understanding; no oversell

## Transitions and conditions

- NODE 06: Valid timed package chosen and caller wants schedule
- NODE 02: Licensing prerequisite uncertainty
- NODE 09: Information complete or self-paced secure enrollment next step explained
- NODE 01: Explicit unrelated new goal; route semantically
- NODE 08: Human requested, private/unknown policy, unavailable action or repeated failure

## Failure behavior / human handoff

Prerequisites unclear → 02; critical preparation/allocation unknown → 08; ready schedule → 06

## Interrupt handling

Stop speaking on interruption. Distinguish clarification, temporary detour and changed goal. Preserve answered context; save previous_persona/resume_goal for detour. Preserve pending_action/request_id/idempotency_key and reconcile before conflicting action.

## Test cases

T05, T06, T10

