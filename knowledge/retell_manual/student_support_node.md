# NODE 07 — Existing Student Support

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

## Purpose

Triage support without inventing private records

## Entry conditions

Paid course, account, certificate or support issue

## Node type

Conversation

## Prompt blueprint / response strategy

Classify public FAQ, instruction, booking change, access, payment, certificate, account or high risk. Public FAQ/instruction uses reviewed knowledge; booking change → 06. Private issues require approved authenticated support tool or staff; none exists now. Do not claim payment received, active enrollment, issued certificate, refund or reset from caller statement. Parent role does not verify account authority. Do not collect credentials or promise ticket submission.

## Read variables

`support_issue`, `support_category`, `verification_status`, `verified_customer_ref`, `booking_reference_input`, `appointment_id`, `package_id`, `previous_persona`, `resume_goal`

## Write variables

`support_issue`, `support_category`, `escalation_reason`, `booking_reference_input`, `active_persona`, `previous_persona`, `resume_goal`

## Required information / questions

Before asking, check populated state; ask again only to resolve contradiction or confirm critical action.

- Minimal symptom: what happens when you try to access the course?
- Course/service only if unknown; no password or card details

## Knowledge sources

knowledge/faq.md; knowledge/policies.md; knowledge/retell_support/unresolved_information.md

## Tools

None; knowledge-only dialogue.

## Exit / success criteria

Public issue answered or minimal issue/reason routed to staff

## Transitions and conditions

- NODE 06: Booking change
- NODE 09: Public FAQ answered
- NODE 01: Explicit unrelated new goal; route semantically
- NODE 08: Human requested, private/unknown policy, unavailable action or repeated failure

## Failure behavior / human handoff

Private/access/payment/certificate/account or unknown policy → 08

## Interrupt handling

Stop speaking on interruption. Distinguish clarification, temporary detour and changed goal. Preserve answered context; save previous_persona/resume_goal for detour. Preserve pending_action/request_id/idempotency_key and reconcile before conflicting action.

## Test cases

T16, T20, T21

