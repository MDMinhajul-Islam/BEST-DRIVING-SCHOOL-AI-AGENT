# Retell manual implementation sheet

**One agent. Nine nodes. Six specialist responsibilities (02–07).** Global rules are agent configuration, not NODE 00 on the canvas. Default mode is production-safe; tools are local only until an approved wrapper exists. Keep variable_registry.md and transitions.md beside this sheet.

## NODE 01

**Retell display name:** 01 Greeting / Main Router

**Purpose/type:** Semantic intent classification with minimal clarification / Subagent

**Prompt file:** knowledge/retell_build/prompts/01_router_prompt.md

**Variables read:** age, student_or_parent, primary_intent, package_id, support_issue

**Variables written/received:** age, student_or_parent, primary_intent, escalation_reason; tool-only outcome fields cannot be caller extraction.

**Knowledge attached:** knowledge/business_overview.md; knowledge/locations.md

**Tools attached:** Built-in Extract Dynamic Variable for allowed caller facts

**Outgoing transitions / condition:** L01 → 02: The caller seeks Texas licensing guidance or cannot identify the licensing pathway before a service recommendation.; L02 → 03: The caller clearly wants adult education or adult driving lessons; student is 18 or older when age determines the service.; L03 → 04: The caller seeks teen education, teen behind-the-wheel or parent-taught support; student is under 18 when age determines service.; L04 → 05: The caller is considering the road test itself or a preparation-plus-test option.; L05 → 06: The caller explicitly asks about availability, booking, an existing appointment, rescheduling or cancellation.; L06 → 07: The caller has a course, payment, access, certificate or other existing-student issue rather than an appointment operation.

**Shared transitions:** G1 → 08, G2 → 09; exact global conditions in transitions.md.

**Fallback:** Stay for one useful missing clarification; unsupported action or unresolved policy/eligibility → 08, never default success

**Test scenario:** T01/T03/T13

## NODE 02

**Retell display name:** 02 Texas License Guide

**Purpose/type:** Determine pathway before inappropriate selling / Subagent

**Prompt file:** knowledge/retell_build/prompts/02_license_guide_prompt.md

**Variables read:** age, license_status, learner_license_status, driver_education_status, road_test_eligibility, package_id

**Variables written/received:** license_status, learner_license_status, driver_education_status, road_test_eligibility, escalation_reason; tool-only outcome fields cannot be caller extraction.

**Knowledge attached:** knowledge/retell_build/reviewed_license_knowledge.md; knowledge/retell_support/regulatory_response_guardrails.md

**Tools attached:** Built-in Extract Dynamic Variable for allowed caller facts

**Outgoing transitions / condition:** L07 → 03: The relevant adult pathway question is resolved and the caller wants an applicable adult school service.; L08 → 04: The relevant teen pathway question is resolved and the caller wants applicable teen or parent-taught services.; L09 → 05: Test prerequisite understanding is resolved and the caller wants to choose a road-test package.; L10 → 06: A specific licensing detour from Booking is resolved, the chosen timed package is still valid and the caller still wants to continue that appointment task.

**Shared transitions:** G1 → 08, G2 → 09, G3 → 01; exact global conditions in transitions.md.

**Fallback:** Stay for one useful missing clarification; unsupported action or unresolved policy/eligibility → 08, never default success

**Test scenario:** T01/T19

## NODE 03

**Retell display name:** 03 Adult Sales Specialist

**Purpose/type:** Match adult education/lesson needs to actual catalog options / Subagent

**Prompt file:** knowledge/retell_build/prompts/03_adult_sales_prompt.md

**Variables read:** age, license_status, learner_license_status, driver_education_status, package_id, package_name, package_price

**Variables written/received:** package_id, package_name, package_price, escalation_reason; tool-only outcome fields cannot be caller extraction.

**Knowledge attached:** knowledge/adult_services.md; knowledge/retell_manual/catalog_reference.md

**Tools attached:** Built-in Extract Dynamic Variable for allowed caller facts

**Outgoing transitions / condition:** L11 → 06: The caller has selected or accepted a valid timed adult package and explicitly wants to check availability or schedule.

**Shared transitions:** G1 → 08, G2 → 09, G3 → 01; exact global conditions in transitions.md.

**Fallback:** Stay for one useful missing clarification; unsupported action or unresolved policy/eligibility → 08, never default success

**Test scenario:** T02/T08

## NODE 04

**Retell display name:** 04 Teen Sales Specialist

**Purpose/type:** Match teen stage and parent-taught context safely / Subagent

**Prompt file:** knowledge/retell_build/prompts/04_teen_sales_prompt.md

**Variables read:** age, student_or_parent, learner_license_status, driver_education_status, package_id, package_name, package_price

**Variables written/received:** package_id, package_name, package_price, escalation_reason; tool-only outcome fields cannot be caller extraction.

**Knowledge attached:** knowledge/teen_services.md; knowledge/parent_taught.md; knowledge/retell_manual/catalog_reference.md

**Tools attached:** Built-in Extract Dynamic Variable for allowed caller facts

**Outgoing transitions / condition:** L12 → 06: The caller has selected or accepted a valid timed teen package and explicitly wants to check availability or schedule.

**Shared transitions:** G1 → 08, G2 → 09, G3 → 01; exact global conditions in transitions.md.

**Fallback:** Stay for one useful missing clarification; unsupported action or unresolved policy/eligibility → 08, never default success

**Test scenario:** T03/T04/T12

## NODE 05

**Retell display name:** 05 Road Test Sales Specialist

**Purpose/type:** Qualify test intent and compare test-only versus useful preparation / Subagent

**Prompt file:** knowledge/retell_build/prompts/05_road_test_sales_prompt.md

**Variables read:** age, learner_license_status, driver_education_status, road_test_eligibility, package_id, package_name, package_price

**Variables written/received:** package_id, package_name, package_price, escalation_reason; tool-only outcome fields cannot be caller extraction.

**Knowledge attached:** knowledge/road_test.md; knowledge/retell_manual/catalog_reference.md; knowledge/retell_build/reviewed_license_knowledge.md

**Tools attached:** Built-in Extract Dynamic Variable for allowed caller facts

**Outgoing transitions / condition:** L13 → 06: The caller has selected or accepted a valid timed road-test package and explicitly wants to check availability or schedule.; L14 → 02: The caller asks licensing requirements or reveals prerequisite uncertainty that blocks road-test recommendation.

**Shared transitions:** G1 → 08, G2 → 09, G3 → 01; exact global conditions in transitions.md.

**Fallback:** Stay for one useful missing clarification; unsupported action or unresolved policy/eligibility → 08, never default success

**Test scenario:** T05/T06/T10

## NODE 06

**Retell display name:** 06 Booking & Scheduling Specialist

**Purpose/type:** Own availability, selection and guarded appointment operations / Subagent

**Prompt file:** knowledge/retell_build/prompts/06_booking_prompt.md

**Variables read:** age, student_or_parent, package_id, package_name, package_price, road_test_eligibility, preferred_date, preferred_time, session_count_required, session_plan, available_slots, selected_slot, appointment_id, booking_status, support_issue, support_category

**Variables written/received:** preferred_date, preferred_time, session_count_required, session_plan, available_slots, selected_slot, appointment_id, booking_status, escalation_reason; tool-only outcome fields cannot be caller extraction.

**Knowledge attached:** knowledge/retell_build/scheduling_knowledge.md; knowledge/retell_manual/catalog_reference.md

**Tools attached:** Built-in Extract Dynamic Variable for allowed caller facts; booking tools only after approved demo/read wrapper, see tool_mapping.md

**Outgoing transitions / condition:** L15 → 02: A newly unanswered licensing question or prerequisite uncertainty blocks the selected appointment task; the same unresolved question has not already been referred back.; L16 → 07: The issue is course/account access, payment, certificate or instruction rather than an appointment operation.

**Shared transitions:** G1 → 08, G2 → 09, G3 → 01; exact global conditions in transitions.md.

**Fallback:** Stay for one useful missing clarification; unsupported action or unresolved policy/eligibility → 08, never default success

**Test scenario:** T07/T08/T09/T11/T14/T15/T20

## NODE 07

**Retell display name:** 07 Existing Student Support

**Purpose/type:** Triage support without inventing private records / Subagent

**Prompt file:** knowledge/retell_build/prompts/07_student_support_prompt.md

**Variables read:** support_issue, support_category, package_id, appointment_id

**Variables written/received:** support_issue, support_category, escalation_reason; tool-only outcome fields cannot be caller extraction.

**Knowledge attached:** knowledge/faq.md; knowledge/policies.md

**Tools attached:** Built-in Extract Dynamic Variable for allowed caller facts

**Outgoing transitions / condition:** L17 → 06: The caller explicitly wants an appointment lookup/change/cancel or availability operation; a private non-booking support issue has not been misclassified as booking.

**Shared transitions:** G1 → 08, G2 → 09, G3 → 01; exact global conditions in transitions.md.

**Fallback:** Stay for one useful missing clarification; unsupported action or unresolved policy/eligibility → 08, never default success

**Test scenario:** T16/T21

## NODE 08

**Retell display name:** 08 Human Escalation

**Purpose/type:** Explain staff need and verified next step / Subagent

**Prompt file:** knowledge/retell_build/prompts/08_human_escalation_prompt.md

**Variables read:** escalation_reason, support_issue, support_category, package_name, preferred_date, booking_status

**Variables written/received:** escalation_reason; tool-only outcome fields cannot be caller extraction.

**Knowledge attached:** knowledge/locations.md; knowledge/business_overview.md

**Tools attached:** Built-in Extract Dynamic Variable for allowed caller facts

**Outgoing transitions / condition:** No local outgoing edge

**Shared transitions:** G2 → 09, G3 → 01; exact global conditions in transitions.md.

**Fallback:** Stay for one useful missing clarification; unsupported action or unresolved policy/eligibility → 08, never default success

**Test scenario:** T18/T20

## NODE 09

**Retell display name:** 09 End Call

**Purpose/type:** Close with an accurate essential outcome / End (global, closing prompt)

**Prompt file:** knowledge/retell_build/prompts/09_end_call_prompt.md

**Variables read:** package_name, appointment_id, booking_status, escalation_reason

**Variables written/received:** None; tool-only outcome fields cannot be caller extraction.

**Knowledge attached:** None

**Tools attached:** No tool; End closing prompt

**Outgoing transitions / condition:** No local outgoing edge

**Shared transitions:** Terminal; exact global conditions in transitions.md.

**Fallback:** Terminal truthful close

**Test scenario:** T11/T18/T20

## State wiring reminder

01–08 are Subagent nodes to allow built-in state extraction without extra Extract-DV nodes; only 06 gets operational tools. Global 01 reroutes, global 08 handles staff and global 09 ends. Use supported global conditions/exclusions and prompt-based edges. Extract explicit facts only; tool success/appointment/status come from validated response binding. End enables Speak During Execution with the closing prompt. No automatic skip/forward for dialogue.
