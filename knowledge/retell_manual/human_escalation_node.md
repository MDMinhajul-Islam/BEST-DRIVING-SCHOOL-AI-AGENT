# NODE 08 — Human Escalation

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

## Purpose

Explain staff need and verified next step

## Entry conditions

Human requested or safe automation unavailable

## Node type

Conversation (transfer only if later verified/configured)

## Prompt blueprint / response strategy

Set specific reason: write/lookup unavailable, payment/refund dispute, account access, uncertain policy, regulatory edge, failure or human request. Briefly explain why staff is needed. No transfer/CRM/ticket integration exists. Offer verified published school contact from reviewed knowledge; confirm contact/hours before deployment, never invent them. A future transfer/intake must acknowledge success before saying connected or sent. No callback promise without accepted intake. Preserve minimal context, avoid private records. Caller declines → 09.

## Read variables

`escalation_reason`, `support_issue`, `support_category`, `package_id`, `preferred_date`, `booking_reference_input`, `caller_name`, `caller_phone`, `caller_email`, `adapter_mode`, `pending_action`, `last_tool_result`

## Write variables

`escalation_reason`, `caller_name`, `caller_phone`, `caller_email`, `active_persona`

## Required information / questions

Before asking, check populated state; ask again only to resolve contradiction or confirm critical action.

- Would you like the verified school contact information?
- Callback details only with consent and an actual configured intake

## Knowledge sources

knowledge/locations.md; knowledge/business_overview.md; knowledge/policies.md

## Tools

None; knowledge-only dialogue. Human node may use a transfer/intake only after verified manual configuration and explicit tool acknowledgement; none exists today.

## Exit / success criteria

Caller knows unresolved action and actual next step; no fake transfer

## Transitions and conditions

- NODE 09: Verified next step offered or caller declines

## Failure behavior / human handoff

Contact unavailable: acknowledge need without guessing; close politely

## Interrupt handling

Stop speaking on interruption. Distinguish clarification, temporary detour and changed goal. Preserve answered context; save previous_persona/resume_goal for detour. Preserve pending_action/request_id/idempotency_key and reconcile before conflicting action.

## Test cases

T18, T20, T21

