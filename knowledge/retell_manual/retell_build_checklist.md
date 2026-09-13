# Manual Retell build checklist

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

Build order: 1 global rules; 2 state; 3 Router; 4 License Guide; 5 Adult Sales; 6 Teen Sales; 7 Road Sales; 8 Booking; 9 Support; 10 Human; 11 End; 12 transitions; 13 isolated mock/approved read-only wiring; 14 test calls. No production writes.

UI mapping checked 2026-09-13: [Retell flow overview](https://docs.retellai.com/build/conversation-flow/overview) describes global settings, dialogue nodes, tool-capable Subagent nodes, deterministic Function nodes and End nodes. [Global-node guide](https://docs.retellai.com/build/conversation-flow/global-node) describes transitions from anywhere and return conditions. Verify available UI before manual build. NODE 00 is global settings, not an extra routable node.

## NODE 00 — Global Agent Rules

- [ ] Node name: Global Agent Rules
- [ ] Node type: Global settings (conceptual node)
- [ ] Prompt: global_agent_rules.md and persona_prompt_blueprints.md section
- [ ] Variables read: knowledge_snapshot, adapter_mode, production_write_enabled
- [ ] Variables written: knowledge_snapshot
- [ ] Tools: None; knowledge-only dialogue.
- [ ] Transition conditions: Applies globally
- [ ] Fallback transition: Any unresolved safety/capability issue → 08
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Source-grounded answers and no premature action claim

## NODE 01 — Greeting / Main Router

- [ ] Node name: Greeting / Main Router
- [ ] Node type: Conversation
- [ ] Prompt: router_node.md and persona_prompt_blueprints.md section
- [ ] Variables read: primary_intent, secondary_intent, age, package_id, support_issue, previous_persona, resume_goal
- [ ] Variables written: primary_intent, secondary_intent, active_persona, previous_persona, resume_goal, age, student_or_parent
- [ ] Tools: None; knowledge-only dialogue.
- [ ] Transition conditions: 02: First-time Texas/licensing uncertainty; 03: Clear adult education/lessons; 04: Teen/parent or parent-taught service; 05: Road-test service; 06: Availability/new/existing booking/change/cancel; 07: Existing student issue; 08: Human request or unresolved route; 09: Caller done
- [ ] Fallback transition: Unresolved intent or human request → 08; caller done → 09
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Correct specialist with minimum sufficient context

## NODE 02 — Texas License Guide

- [ ] Node name: Texas License Guide
- [ ] Node type: Conversation
- [ ] Prompt: texas_license_guide_node.md and persona_prompt_blueprints.md section
- [ ] Variables read: age, first_time_applicant, license_status, learner_license_status, permit_status, driver_education_status, parent_taught_status, texas_residency_status, out_of_state_license_status, foreign_license_status, impact_texas_status, road_test_eligibility, license_issuing_jurisdiction, license_expiry, learner_issue_date, certificate_type, required_document_status, impact_program, impact_certificate_date, move_date, suspension_during_hold, previous_persona, resume_goal, knowledge_snapshot
- [ ] Variables written: first_time_applicant, license_status, learner_license_status, permit_status, driver_education_status, parent_taught_status, texas_residency_status, out_of_state_license_status, foreign_license_status, impact_texas_status, road_test_eligibility, license_issuing_jurisdiction, license_expiry, learner_issue_date, certificate_type, required_document_status, impact_program, impact_certificate_date, move_date, suspension_during_hold, active_persona, previous_persona, resume_goal
- [ ] Tools: None; knowledge-only dialogue.
- [ ] Transition conditions: 03: Adult pathway resolved; relevant service requested; 04: Teen pathway resolved; relevant service requested; 05: Prerequisites reported; test option requested; 06: Return to saved booking goal after qualification; 09: Advice answered; no sale wanted; 01: Explicit unrelated new goal; route semantically; 08: Human requested, private/unknown policy, unavailable action or repeated failure
- [ ] Fallback transition: Unverified edge/conflict → 08 with official DPS/TDLR referral
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Supported usual pathway explained; eligibility remains reported or needs_review

## NODE 03 — Adult Sales Specialist

- [ ] Node name: Adult Sales Specialist
- [ ] Node type: Conversation
- [ ] Prompt: adult_sales_node.md and persona_prompt_blueprints.md section
- [ ] Variables read: age, driver_education_status, license_status, permit_status, experience_level, program, course_id, course_name, package_id, package_name, package_price, currency, price_snapshot, recommended_service, knowledge_snapshot
- [ ] Variables written: program, course_id, course_name, package_id, package_name, package_price, currency, price_snapshot, recommended_service, experience_level, active_persona
- [ ] Tools: None; knowledge-only dialogue.
- [ ] Transition conditions: 06: Valid timed package chosen and caller wants schedule; 02: Licensing prerequisite uncertainty; 09: Information complete or self-paced secure enrollment next step explained; 01: Explicit unrelated new goal; route semantically; 08: Human requested, private/unknown policy, unavailable action or repeated failure
- [ ] Fallback transition: Licensing uncertainty → 02; current price conflict → 08; schedule → 06
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Valid package chosen or informed decision without pressure

## NODE 04 — Teen Sales Specialist

- [ ] Node name: Teen Sales Specialist
- [ ] Node type: Conversation
- [ ] Prompt: teen_sales_node.md and persona_prompt_blueprints.md section
- [ ] Variables read: age, student_or_parent, driver_education_status, learner_license_status, parent_taught_status, program, course_id, course_name, package_id, package_name, package_price, currency, price_snapshot, recommended_service, knowledge_snapshot
- [ ] Variables written: program, course_id, course_name, package_id, package_name, package_price, currency, price_snapshot, recommended_service, active_persona
- [ ] Tools: None; knowledge-only dialogue.
- [ ] Transition conditions: 06: Valid timed package chosen and caller wants schedule; 02: Licensing prerequisite uncertainty; 09: Information complete or self-paced secure enrollment next step explained; 01: Explicit unrelated new goal; route semantically; 08: Human requested, private/unknown policy, unavailable action or repeated failure
- [ ] Fallback transition: Licensing → 02; transfer/observation/PTDE allocation unknown → 08; schedule → 06
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Stage-appropriate valid package with limitations clear

## NODE 05 — Road Test Sales Specialist

- [ ] Node name: Road Test Sales Specialist
- [ ] Node type: Conversation
- [ ] Prompt: road_test_sales_node.md and persona_prompt_blueprints.md section
- [ ] Variables read: age, road_test_eligibility, learner_license_status, driver_education_status, impact_texas_status, experience_level, program, course_id, course_name, package_id, package_name, package_price, currency, price_snapshot, knowledge_snapshot
- [ ] Variables written: program, course_id, course_name, package_id, package_name, package_price, currency, price_snapshot, recommended_service, experience_level, active_persona
- [ ] Tools: None; knowledge-only dialogue.
- [ ] Transition conditions: 06: Valid timed package chosen and caller wants schedule; 02: Licensing prerequisite uncertainty; 09: Information complete or self-paced secure enrollment next step explained; 01: Explicit unrelated new goal; route semantically; 08: Human requested, private/unknown policy, unavailable action or repeated failure
- [ ] Fallback transition: Prerequisites unclear → 02; critical preparation/allocation unknown → 08; ready schedule → 06
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Appropriate choice and prerequisite understanding; no oversell

## NODE 06 — Booking & Scheduling Specialist

- [ ] Node name: Booking & Scheduling Specialist
- [ ] Node type: Subagent (tool-capable dialogue, manually gated tools)
- [ ] Prompt: booking_node.md and persona_prompt_blueprints.md section
- [ ] Variables read: package_id, package_name, package_price, age, road_test_eligibility, preferred_location, preferred_date, preferred_time, session_count_required, session_plan, available_slots, selected_slot, selected_sessions, appointment_id, booking_status, booking_version, location_id, school_timezone, adapter_mode, last_tool_result, production_write_enabled, backend_success_verified, booking_reference_input, verified_customer_ref, verification_status, request_id, idempotency_key, tool_failure_count, pending_action, previous_persona, resume_goal
- [ ] Variables written: preferred_location, preferred_date, preferred_time, session_count_required, session_plan, available_slots, selected_slot, selected_sessions, appointment_id, booking_status, booking_version, location_id, last_tool_result, backend_success_verified, booking_reference_input, verified_customer_ref, verification_status, request_id, idempotency_key, tool_failure_count, pending_action, escalation_reason, active_persona, previous_persona, resume_goal
- [ ] Tools: Normalized check_availability, create_booking, find_booking, reschedule_booking, cancel_booking. Demo: synthetic mock through a future test wrapper. Production-safe: approved read-only availability only; lookup/writes blocked. Nothing wired into Retell today. Permissions enforced server-side, never by caller prompt.
- [ ] Transition conditions: 02: Eligibility question/uncertainty; 07: Account/course support emerges; 09: Observation or confirmed correct-mode result complete; 01: Explicit unrelated new goal; route semantically; 08: Human requested, private/unknown policy, unavailable action or repeated failure
- [ ] Fallback transition: Unavailable write/verification/lookup, alignment gap, unknown policy or repeated failure → 08; licensing → 02; account → 07
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Reads never confirm booking; real confirmation requires authorized explicit production success and identity; mock confirmation always demo

## NODE 07 — Existing Student Support

- [ ] Node name: Existing Student Support
- [ ] Node type: Conversation
- [ ] Prompt: student_support_node.md and persona_prompt_blueprints.md section
- [ ] Variables read: support_issue, support_category, verification_status, verified_customer_ref, booking_reference_input, appointment_id, package_id, previous_persona, resume_goal
- [ ] Variables written: support_issue, support_category, escalation_reason, booking_reference_input, active_persona, previous_persona, resume_goal
- [ ] Tools: None; knowledge-only dialogue.
- [ ] Transition conditions: 06: Booking change; 09: Public FAQ answered; 01: Explicit unrelated new goal; route semantically; 08: Human requested, private/unknown policy, unavailable action or repeated failure
- [ ] Fallback transition: Private/access/payment/certificate/account or unknown policy → 08
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Public issue answered or minimal issue/reason routed to staff

## NODE 08 — Human Escalation

- [ ] Node name: Human Escalation
- [ ] Node type: Conversation (transfer only if later verified/configured)
- [ ] Prompt: human_escalation_node.md and persona_prompt_blueprints.md section
- [ ] Variables read: escalation_reason, support_issue, support_category, package_id, preferred_date, booking_reference_input, caller_name, caller_phone, caller_email, adapter_mode, pending_action, last_tool_result
- [ ] Variables written: escalation_reason, caller_name, caller_phone, caller_email, active_persona
- [ ] Tools: None; knowledge-only dialogue. Human node may use a transfer/intake only after verified manual configuration and explicit tool acknowledgement; none exists today.
- [ ] Transition conditions: 09: Verified next step offered or caller declines
- [ ] Fallback transition: Contact unavailable: acknowledge need without guessing; close politely
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Caller knows unresolved action and actual next step; no fake transfer

## NODE 09 — End Call

- [ ] Node name: End Call
- [ ] Node type: End (short final utterance)
- [ ] Prompt: end_call_node.md and persona_prompt_blueprints.md section
- [ ] Variables read: booking_status, appointment_id, backend_success_verified, adapter_mode, last_tool_result, escalation_reason, pending_action, package_name, support_issue
- [ ] Variables written: active_persona
- [ ] Tools: None; knowledge-only dialogue.
- [ ] Transition conditions: Applies globally
- [ ] Fallback transition: Human request returns to 08; otherwise state next action clearly
- [ ] Interrupt handling: Enable supported barge-in; preserve context, save detour, reconcile pending tool before new action
- [ ] End conditions: Short truthful ending

## Integration acceptance

- [ ] Bind only reviewed specialist sources; suppress review-required regulatory records.
- [ ] Configure defined state types/clearing and catalog-owned prices; backend guards must not rely on free-text extraction.
- [ ] Deploy approved authenticated wrapper before tool wiring; current adapters are not HTTP services.
- [ ] Keep synthetic mock separate from production; secure verification and credentials stay server-side.
- [ ] Omit or hard-reject production lookup/create/reschedule/cancel; allow only approved read adapter.
- [ ] Validate timezone, stable IDs, duration/resource compatibility and road-test schedule origin before future binding actions.
- [ ] Optional deterministic Function utility nodes may be added after real API contracts exist; no speculative tools.
- [ ] Verify contact/hours and actual transfer/intake acknowledgement before enabling human tools.
- [ ] Run all planned calls, record actual pass/fail and recordings. No executed calls claimed here.
