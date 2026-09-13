# Manual test-call matrix

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

Expected outcomes only, not executed calls. Covers the original assignment’s mandatory challenges plus multi-session/remainder/road-allocation checks. Human builders must record at least 14 actual call results and three demo recordings (sales→booking, booking/reschedule, support/recovery) after manual deployment.

## T01 — Adult first-time, 19, unsure where to start

**Starting Node:** 01

**Questions:** Do not re-ask age; current credential/education, residency as needed

**Variables:** age, first_time_applicant, license_status, driver_education_status

**Transitions:** 01 → 02 → 03 or 09

**Tools:** 

**Expected Outcome:** Reviewed usual pathway; no mandatory purchase invented

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T02 — Adult permit and nervous driver

**Starting Node:** 01

**Questions:** Age if missing, skill/confidence goal

**Variables:** age, permit_status, experience_level, package_id

**Transitions:** 01 → 03 → 06

**Tools:** check_availability

**Expected Outcome:** Appropriate catalog lesson comparison, no readiness guarantee or real booking

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T03 — Parent with daughter 15

**Starting Node:** 01

**Questions:** Education/learner stage, not supplied age again

**Variables:** age, student_or_parent, driver_education_status

**Transitions:** 01 → 04 → 02 if needed

**Tools:** 

**Expected Outcome:** Teen path, no immediate road-test promise

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T04 — Teen partial education elsewhere

**Starting Node:** 01

**Questions:** Completed stage/certificate category, age if missing

**Variables:** age, driver_education_status, certificate_type, parent_taught_status

**Transitions:** 01 → 04 → 02 or 08

**Tools:** 

**Expected Outcome:** No inferred transfer acceptance; BTW only if suitable

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T05 — Ready driver wants test only

**Starting Node:** 01

**Questions:** Only missing prerequisites

**Variables:** road_test_eligibility, package_id

**Transitions:** 01 → 05 → 06

**Tools:** check_availability

**Expected Outcome:** Test-only if appropriate; no pressured preparation or real reservation

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T06 — Test soon, cannot parallel park or prerequisites unclear

**Starting Node:** 01

**Questions:** Confidence and prerequisite gap

**Variables:** experience_level, road_test_eligibility

**Transitions:** 01 → 05 → 02 or 08

**Tools:** 

**Expected Outcome:** Reasonable preparation option; no guaranteed eligibility

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T07 — Saturday afternoon availability

**Starting Node:** 01

**Questions:** Missing service/date; resolve relative date in agreed timezone

**Variables:** preferred_date, preferred_time, package_id, available_slots, booking_status

**Transitions:** 01 → 06 → 09 or 08

**Tools:** check_availability

**Expected Outcome:** Approved provisional read only; no static knowledge or reservation

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T08 — Adult six-hour multi-session

**Starting Node:** 03

**Questions:** Missing preferences; discuss three tentative sessions

**Variables:** package_id, session_count_required, session_plan, selected_sessions, booking_status

**Transitions:** 03 → 06 → 08 production / 09 demo

**Tools:** check_availability, create_booking

**Expected Outcome:** [120,120,120]; separate per-session outcomes, no assumed atomic school booking

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T09 — Teen seven-hour driving

**Starting Node:** 04

**Questions:** Driving dates separate from observation allocation

**Variables:** session_count_required, session_plan, selected_sessions

**Transitions:** 04 → 06 → 08 production

**Tools:** check_availability

**Expected Outcome:** [120,120,120,60], four driving sessions; observation not converted

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T10 — Road-test interval with contradictory live labels

**Starting Node:** 05

**Questions:** Preferred date; keep buffers internal

**Variables:** package_id, selected_slot, booking_status

**Transitions:** 05 → 06 → 08

**Tools:** check_availability

**Expected Outcome:** 20+5+5=30 business rule; no rounded/fabricated starts; verify backend origin

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T11 — Move Tuesday appointment to Thursday

**Starting Node:** 01

**Questions:** Known reference; future secure verification, no private enumeration

**Variables:** booking_reference_input, verification_status, pending_action

**Transitions:** 01 → 06 → 08 production / 09 demo

**Tools:** find_booking, check_availability, reschedule_booking

**Expected Outcome:** Production unavailable; demo verified and version-checked, no early success

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T12 — Teen price challenge: I thought it was $299

**Starting Node:** 04

**Questions:** Which teen package only if ambiguous

**Variables:** package_id, package_price, price_snapshot

**Transitions:** 04 → 04 or 08

**Tools:** 

**Expected Outcome:** Catalog check: full snapshot $399, BTW $350; never overwrite from caller claim

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T13 — Mid-call adult sales to existing test reschedule

**Starting Node:** 03

**Questions:** Existing reference only if missing

**Variables:** primary_intent, previous_persona, resume_goal, booking_reference_input

**Transitions:** 03 → 01 → 06

**Tools:** find_booking

**Expected Outcome:** Preserve context; no repeated age/package question; staff fallback today

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T14 — Slot taken after selection

**Starting Node:** 06

**Questions:** Refresh choices and obtain new selection

**Variables:** selected_slot, available_slots, booking_status, last_tool_result

**Transitions:** 06 → 06 or 08

**Tools:** create_booking, check_availability

**Expected Outcome:** SLOT_NO_LONGER_AVAILABLE; never success or blind retry

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T15 — Tool timeout/API failure

**Starting Node:** 06

**Questions:** One useful read retry, no repeated writes

**Variables:** tool_failure_count, pending_action, request_id, idempotency_key

**Transitions:** 06 → 08

**Tools:** check_availability, create_booking

**Expected Outcome:** Write timeout outcome unknown; preserve key/reconcile; read retry at most once

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T16 — Paid online course inaccessible

**Starting Node:** 01

**Questions:** Minimal symptom and course, no password/card

**Variables:** support_category, support_issue, escalation_reason

**Transitions:** 01 → 07 → 08

**Tools:** 

**Expected Outcome:** No payment/enrollment/account assertion; staff required

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T17 — Off-topic or unclear caller

**Starting Node:** 01

**Questions:** One brief school-service clarification

**Variables:** primary_intent, escalation_reason

**Transitions:** 01 → 01 → 08 or 09

**Tools:** 

**Expected Outcome:** Polite redirect, no invented service/endless loop

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T18 — Human explicitly requested

**Starting Node:** 03

**Questions:** Reason optional, no forced sales qualification

**Variables:** escalation_reason

**Transitions:** 03 → 08 → 09

**Tools:** 

**Expected Outcome:** Immediate staff path; no transfer/callback claim without acknowledgement

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T19 — Foreign credential edge or contradictory age

**Starting Node:** 02

**Questions:** Country/validity/residency categories; resolve contradiction

**Variables:** license_issuing_jurisdiction, license_status, age, road_test_eligibility

**Transitions:** 02 → 08

**Tools:** 

**Expected Outcome:** Reviewed rule only; no exemption invented

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T20 — Cancel and refund request

**Starting Node:** 01

**Questions:** Known reference, reason optional

**Variables:** pending_action, booking_reference_input, verification_status, escalation_reason

**Transitions:** 01 → 06 → 08 production / 09 demo

**Tools:** find_booking, cancel_booking

**Expected Outcome:** Real cancel/refund blocked; synthetic cancellation releases fixtures, no refund implied

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

## T21 — Certificate/account issue, parent caller

**Starting Node:** 07

**Questions:** Issue category, no private record disclosure

**Variables:** support_category, verification_status, escalation_reason

**Transitions:** 07 → 08

**Tools:** 

**Expected Outcome:** Parent relationship not verified authority; no certificate/account assertions

**Execution Status:** DESIGN ONLY — manual call not run

**Actual result / recording / pass-fail:** Pending manual build.

