# NODE 09 — End Call

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

## Purpose

Close with an accurate essential outcome

## Entry conditions

Caller finished or escalation next step agreed

## Node type

End (short final utterance)

## Prompt blueprint / response strategy

Summarize only essential confirmed outcome, no full recap. A real appointment statement requires BOOKING_CONFIRMED, appointment_id and explicit authorized production success; demo always labeled demo. Cancelled result is not active reservation. Unresolved booking/payment/account action remains unresolved; no claimed callback or submission. Pending write outcome is unknown and needs reconciliation. End naturally without repeated questions.

## Read variables

`booking_status`, `appointment_id`, `backend_success_verified`, `adapter_mode`, `last_tool_result`, `escalation_reason`, `pending_action`, `package_name`, `support_issue`

## Write variables

`active_persona`

## Required information / questions

No mandatory questions; check known state first.

## Knowledge sources

knowledge/retell_manual/booking_state_machine.md

## Tools

None; knowledge-only dialogue.

## Exit / success criteria

Short truthful ending

## Transitions and conditions

Global configuration applies to all nodes; no routable edge.

## Failure behavior / human handoff

Human request returns to 08; otherwise state next action clearly

## Interrupt handling

Stop speaking on interruption. Distinguish clarification, temporary detour and changed goal. Preserve answered context; save previous_persona/resume_goal for detour. Preserve pending_action/request_id/idempotency_key and reconcile before conflicting action.

## Test cases

T11, T18, T20

