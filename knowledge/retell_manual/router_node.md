# NODE 01 — Greeting / Main Router

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

## Purpose

Semantic intent classification with minimal clarification

## Entry conditions

Start call or explicit unrelated goal switch

## Node type

Conversation

## Prompt blueprint / response strategy

Classify goals by meaning, not keyword presence. First-time Texas licensing uncertainty → 02 before sales. Clear adult education/lessons → 03; teen/parent or parent-taught service → 04; road test → 05; availability/new/existing booking/reschedule/cancel → 06; paid course/account support → 07. Pricing follows relevant sales; location follows selected service or Booking, distinguishing advertised areas from branches/pickup. Do not perform full sales qualification. Ask one useful clarification, then staff if still unresolved. Politely redirect off-topic once; avoid endless loops.

## Read variables

`primary_intent`, `secondary_intent`, `age`, `package_id`, `support_issue`, `previous_persona`, `resume_goal`

## Write variables

`primary_intent`, `secondary_intent`, `active_persona`, `previous_persona`, `resume_goal`, `age`, `student_or_parent`

## Required information / questions

Before asking, check populated state; ask again only to resolve contradiction or confirm critical action.

- Thanks for calling Best Driving School. How can I help?
- Practice request with unknown age: How old is the student?
- Ambiguous price/location: Which service are you considering?

## Knowledge sources

knowledge/retell_support/router_intent_reference.md; knowledge/locations.md

## Tools

None; knowledge-only dialogue.

## Exit / success criteria

Correct specialist with minimum sufficient context

## Transitions and conditions

- NODE 02: First-time Texas/licensing uncertainty
- NODE 03: Clear adult education/lessons
- NODE 04: Teen/parent or parent-taught service
- NODE 05: Road-test service
- NODE 06: Availability/new/existing booking/change/cancel
- NODE 07: Existing student issue
- NODE 08: Human request or unresolved route
- NODE 09: Caller done

## Failure behavior / human handoff

Unresolved intent or human request → 08; caller done → 09

## Interrupt handling

Stop speaking on interruption. Distinguish clarification, temporary detour and changed goal. Preserve answered context; save previous_persona/resume_goal for detour. Preserve pending_action/request_id/idempotency_key and reconcile before conflicting action.

## Test cases

T01, T03, T07, T13, T17

