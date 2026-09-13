# Shared state — final recommended dictionary

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

Unset values are null/unknown. Reported licensing facts are not verified account facts. Optional contact is not needed for advice/prices. No passwords, cards, DOB, document numbers or verification tokens. Compatibility aliases have one source of truth: permit_status mirrors learner_license_status; foreign/out-of-state views derive from license and jurisdiction. Legacy intent → primary_intent, selected_package → package_id, texas_resident_status → texas_residency_status, previous_intent → resume_goal, selected_slot_id → selected_slot.slot_id.

## Caller

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `caller_name` | caller name | 01, 07, 08 | 01, 07, 08, 09 | Optional | End call under approved retention; never public logs |
| `caller_phone` | Callback with consent only; not verification | 01, 07, 08 | 01, 07, 08, 09 | Optional | End call under approved retention; never public logs |
| `caller_email` | Optional callback/enrollment contact; not verification | 01, 07, 08 | 01, 07, 08, 09 | Optional | End call under approved retention; never public logs |

## Student

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `student_name` | student name | 01, 02, 03, 04 | 01, 02, 03, 04, 05, 06, 07 | Conditional | Student changes: clear licensing, verification, package and tentative slots |
| `student_or_parent` | student / parent / other | 01, 02, 03, 04 | 01, 02, 03, 04, 05, 06, 07 | Conditional | Student changes: clear licensing, verification, package and tentative slots |
| `age` | Explicit student age; do not infer from package | 01, 02, 03, 04 | 01, 02, 03, 04, 05, 06, 07 | Conditional | Student changes: clear licensing, verification, package and tentative slots |

## Licensing

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `first_time_applicant` | first time applicant | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `license_status` | license status | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `learner_license_status` | learner license status | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `permit_status` | Compatibility view of learner_license_status; update together | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `driver_education_status` | driver education status | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `parent_taught_status` | parent taught status | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `texas_residency_status` | texas residency status | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `out_of_state_license_status` | Derived from license_status and jurisdiction | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `foreign_license_status` | Derived from license_status and jurisdiction | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `impact_texas_status` | impact texas status | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |
| `road_test_eligibility` | unknown / prerequisites_reported / needs_review; never government-approved | 02 | 02, 03, 04, 05, 06 | Conditional | Student/age/credential changes; requalify affected pathway |

## Licensing details

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `license_issuing_jurisdiction` | license issuing jurisdiction | 02 | 02, 04, 05 | Conditional | Changed credential/student; ask only if applicable reviewed rule needs it |
| `license_expiry` | license expiry | 02 | 02, 04, 05 | Conditional | Changed credential/student; ask only if applicable reviewed rule needs it |
| `learner_issue_date` | learner issue date | 02 | 02, 04, 05 | Conditional | Changed credential/student; ask only if applicable reviewed rule needs it |
| `certificate_type` | certificate type | 02 | 02, 04, 05 | Conditional | Changed credential/student; ask only if applicable reviewed rule needs it |
| `required_document_status` | required document status | 02 | 02, 04, 05 | Conditional | Changed credential/student; ask only if applicable reviewed rule needs it |
| `impact_program` | impact program | 02 | 02, 04, 05 | Conditional | Changed credential/student; ask only if applicable reviewed rule needs it |
| `impact_certificate_date` | impact certificate date | 02 | 02, 04, 05 | Conditional | Changed credential/student; ask only if applicable reviewed rule needs it |
| `move_date` | move date | 02 | 02, 04, 05 | Conditional | Changed credential/student; ask only if applicable reviewed rule needs it |
| `suspension_during_hold` | suspension during hold | 02 | 02, 04, 05 | Conditional | Changed credential/student; ask only if applicable reviewed rule needs it |

## Intent

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `primary_intent` | Current semantic action goal | 01, 02, 03, 04, 05, 06, 07, 08 | 01, 02, 03, 04, 05, 06, 07, 08, 09 | Required | New call; consume completed detour; explicit new goal changes primary intent |
| `secondary_intent` | Deferred explicit goal | 01, 02, 03, 04, 05, 06, 07, 08 | 01, 02, 03, 04, 05, 06, 07, 08, 09 | Required | New call; consume completed detour; explicit new goal changes primary intent |
| `active_persona` | Current node ID | 01, 02, 03, 04, 05, 06, 07, 08 | 01, 02, 03, 04, 05, 06, 07, 08, 09 | Required | New call; consume completed detour; explicit new goal changes primary intent |
| `previous_persona` | Saved valid prior node ID | 01, 02, 03, 04, 05, 06, 07, 08 | 01, 02, 03, 04, 05, 06, 07, 08, 09 | Required | New call; consume completed detour; explicit new goal changes primary intent |
| `resume_goal` | Minimal suspended task and dependencies | 01, 02, 03, 04, 05, 06, 07, 08 | 01, 02, 03, 04, 05, 06, 07, 08, 09 | Required | New call; consume completed detour; explicit new goal changes primary intent |

## Sales

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `program` | program | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |
| `course_id` | course id | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |
| `course_name` | course name | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |
| `package_id` | Canonical catalog ID, never provisional form ID | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |
| `package_name` | package name | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |
| `package_price` | Numeric catalog base price, caller cannot overwrite | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |
| `recommended_service` | recommended service | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |
| `currency` | currency | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |
| `price_snapshot` | Reviewed catalog source/version | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |
| `experience_level` | Caller-reported confidence and training goal | 03, 04, 05 | 01, 02, 03, 04, 05, 06, 09 | Conditional | Package changes clear session plan and tentative availability; preserve unrelated verified existing booking |

## Booking

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `preferred_location` | Caller area preference, not operational ID or pickup commitment | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `preferred_date` | Caller-confirmed ISO date in agreed school timezone | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `preferred_time` | preferred time | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `session_count_required` | Known derived driving count; null for unresolved PTDE/preparation | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `session_plan` | Ordered minute durations from known business plan; observation separate | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `available_slots` | Ephemeral returned observations; never static knowledge | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `selected_slot` | Returned authoritative object; never fabricate an ID from a label | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `selected_sessions` | Ordered tentative selections with duration/provenance | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `appointment_id` | Verified backend result only, not caller-entered reference | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `booking_status` | Guarded enum in booking_state_machine.md | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |
| `booking_version` | Backend concurrency version; mock version synthetic | 06 | 03, 04, 05, 06, 07, 08, 09 | Conditional | Date/location/package/resource changes invalidate tentative slots; expire according to approved backend freshness, no invented TTL |

## Booking guards

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `location_id` | Authoritative operational ID only; unknown today | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `school_timezone` | Owner/backend-confirmed IANA string; unknown in current payload | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `adapter_mode` | Builder-set demo_mock / production_safe | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `last_tool_result` | Sanitized normalized result including mode/confirmation/error | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `production_write_enabled` | Secure server configuration; false today | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `backend_success_verified` | Server-derived explicit correct-environment success and appointment ID gate | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `booking_reference_input` | Caller-reported known reference; not verified appointment identity | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `verified_customer_ref` | Scoped secure identity; no credentials/tokens in conversation state | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `request_id` | Server-issued non-PII trace ID | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `idempotency_key` | Server-issued same-action retry key | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `tool_failure_count` | tool failure count | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |
| `pending_action` | create / find / reschedule / cancel / none | 06 | 06, 07, 08, 09 | Conditional | New action/context clears success/result/key; preserve in-flight action and key on interruption until reconciled |

## Support

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `support_issue` | Minimal caller symptom, not verified account facts | 06, 07, 08 | 06, 07, 08, 09 | Conditional | Student/customer changes clear verification; new issue resets reason/category |
| `support_category` | faq / instruction / booking_change / access / payment / certificate / account / high_risk | 06, 07, 08 | 06, 07, 08, 09 | Conditional | Student/customer changes clear verification; new issue resets reason/category |
| `verification_status` | unverified / verified / failed; secure system sets verified | 06, 07, 08 | 06, 07, 08, 09 | Conditional | Student/customer changes clear verification; new issue resets reason/category |
| `escalation_reason` | Specific reason staff needed; not proof ticket or transfer occurred | 06, 07, 08 | 06, 07, 08, 09 | Conditional | Student/customer changes clear verification; new issue resets reason/category |

## Source control

| Variable | Purpose | Set by NODE | Read by NODE | Required | Clear when |
| --- | --- | --- | --- | --- | --- |
| `knowledge_snapshot` | Reviewed business/regulatory source version and freshness gate | 00 | 01, 02, 03, 04, 05, 06, 07, 08, 09 | Required | Builder changes reviewed source set; never caller-controlled |

## Types, defaults and trust

IDs/names/contact nullable strings; age integer; first_time_applicant nullable boolean; licensing/intent/support values precise categories. Prices numeric USD, source read-only. Dates ISO YYYY-MM-DD. session_plan ordered minute integers; selected_sessions ordered tentative slot/duration/provenance objects; available_slots ephemeral list. school_timezone owner-confirmed IANA string. Defaults: verification_status=unverified, booking_status=NO_PACKAGE, tool_failure_count=0, backend_success_verified=false, production_write_enabled=false. Server/configuration owns adapter_mode, timezone, verified IDs, versions, request keys, permissions and explicit success; the model must not set them from caller claims. Although NODE 06 consumes these values, its writes are restricted to validated tool/state events.

Changing student clears licensing/verification/sales/tentative booking context. Changing package clears tentative session/slot selections, not a separate verified existing appointment. Temporary detours preserve tentative context only; revalidate when returning. End call cleanup follows approved retention; no private state in public knowledge.
