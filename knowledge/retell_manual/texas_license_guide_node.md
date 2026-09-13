# NODE 02 — Texas License Guide

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

## Purpose

Determine pathway before inappropriate selling

## Entry conditions

Licensing uncertainty, jurisdiction edge or missing prerequisite

## Node type

Conversation

## Prompt blueprint / response strategy

Use progressive questions, not the entire checklist. Identify adult/teen/new-resident/international/parent-taught branch from reported facts. Retrieve applicable reviewed pathway/rule conditions; give one plain-language next step. Distinguish education, instruction, practice, skills test and DPS issuance. Do not guarantee government eligibility or transfer/provider acceptance. Changed age/credential invalidates dependent qualification. Return to saved goal after resolution. Advice does not require a purchase. Suppress disputed and review-required details.

## Read variables

`age`, `first_time_applicant`, `license_status`, `learner_license_status`, `permit_status`, `driver_education_status`, `parent_taught_status`, `texas_residency_status`, `out_of_state_license_status`, `foreign_license_status`, `impact_texas_status`, `road_test_eligibility`, `license_issuing_jurisdiction`, `license_expiry`, `learner_issue_date`, `certificate_type`, `required_document_status`, `impact_program`, `impact_certificate_date`, `move_date`, `suspension_during_hold`, `previous_persona`, `resume_goal`, `knowledge_snapshot`

## Write variables

`first_time_applicant`, `license_status`, `learner_license_status`, `permit_status`, `driver_education_status`, `parent_taught_status`, `texas_residency_status`, `out_of_state_license_status`, `foreign_license_status`, `impact_texas_status`, `road_test_eligibility`, `license_issuing_jurisdiction`, `license_expiry`, `learner_issue_date`, `certificate_type`, `required_document_status`, `impact_program`, `impact_certificate_date`, `move_date`, `suspension_during_hold`, `active_persona`, `previous_persona`, `resume_goal`

## Required information / questions

Before asking, check populated state; ask again only to resolve contradiction or confirm critical action.

- Age only if unknown; first-time applicant only if relevant
- Current learner license or other driver license?
- Ask jurisdiction, residency or education stage next only as pathway needs it

## Knowledge sources

knowledge/regulatory/README.md; knowledge/regulatory/adult_first_time_license.md; knowledge/regulatory/teen_license_pathway.md; knowledge/regulatory/new_texas_residents.md; knowledge/regulatory/international_drivers.md; knowledge/regulatory/parent_taught_driver_education.md; knowledge/retell_support/regulatory_response_guardrails.md

## Tools

None; knowledge-only dialogue.

## Exit / success criteria

Supported usual pathway explained; eligibility remains reported or needs_review

## Transitions and conditions

- NODE 03: Adult pathway resolved; relevant service requested
- NODE 04: Teen pathway resolved; relevant service requested
- NODE 05: Prerequisites reported; test option requested
- NODE 06: Return to saved booking goal after qualification
- NODE 09: Advice answered; no sale wanted
- NODE 01: Explicit unrelated new goal; route semantically
- NODE 08: Human requested, private/unknown policy, unavailable action or repeated failure

## Failure behavior / human handoff

Unverified edge/conflict → 08 with official DPS/TDLR referral

## Interrupt handling

Stop speaking on interruption. Distinguish clarification, temporary detour and changed goal. Preserve answered context; save previous_persona/resume_goal for detour. Preserve pending_action/request_id/idempotency_key and reconcile before conflicting action.

## Test cases

T01, T06, T19

