# Handoff context

Carry known answers silently; no new greeting. Fields are semantic context, not a demand to populate every field before routing. Conditional fields may remain in transcript until that pathway is enabled. Sales supplies selected package; Booking calculates/reads the sourced plan on entry when not already present.

| From | To | Carry if known | On entry |
| --- | --- | --- | --- |
| 01 | 02 | age, license_status, learner_license_status, driver_education_status | Reuse known values; ask only the next relevant missing fact |
| 01 | 03 | age, learner_license_status, driver_education_status | Reuse known values; ask only the next relevant missing fact |
| 01 | 04 | age, student_or_parent, driver_education_status, parent_taught_status | Reuse known values; ask only the next relevant missing fact |
| 01 | 05 | age, learner_license_status, road_test_eligibility | Reuse known values; ask only the next relevant missing fact |
| 01 | 06 | package_id, package_name, preferred_date, preferred_time, booking_reference_input | Reuse known values; ask only the next relevant missing fact |
| 01 | 07 | support_issue, support_category, package_id | Reuse known values; ask only the next relevant missing fact |
| 02 | 03 | age, license_status, learner_license_status, driver_education_status | Reuse known values; ask only the next relevant missing fact |
| 02 | 04 | age, student_or_parent, learner_license_status, driver_education_status, parent_taught_status | Reuse known values; ask only the next relevant missing fact |
| 02 | 05 | road_test_eligibility, learner_license_status, driver_education_status, impact_texas_status | Reuse known values; ask only the next relevant missing fact |
| 02 | 06 | package_id, package_name, package_price, road_test_eligibility, preferred_date, preferred_time, previous_persona | Reuse known values; ask only the next relevant missing fact |
| 03 | 06 | age, student_or_parent, package_id, package_name, package_price, session_count_required, session_plan | Reuse known values; ask only the next relevant missing fact |
| 04 | 06 | age, student_or_parent, package_id, package_name, package_price, session_count_required, session_plan | Reuse known values; ask only the next relevant missing fact |
| 05 | 06 | age, student_or_parent, package_id, package_name, package_price, session_count_required, session_plan | Reuse known values; ask only the next relevant missing fact |
| 05 | 02 | age, learner_license_status, driver_education_status, road_test_eligibility | Reuse known values; ask only the next relevant missing fact |
| 06 | 02 | age, package_id, road_test_eligibility, previous_persona | Reuse known values; ask only the next relevant missing fact |
| 06 | 07 | support_issue, support_category, package_id | Reuse known values; ask only the next relevant missing fact |
| 07 | 06 | support_issue, support_category, booking_reference_input, appointment_id | Reuse known values; ask only the next relevant missing fact |

Global reroute carries the current goal and known facts without automatically keeping a return stack. Human receives minimal issue/package/preference and explicit reason, not secrets/private records. End receives only confirmed result or unresolved next action. Changed student invalidates prior qualification, verification and tentative package/slots; changed package/date invalidates tentative slots, not a separate existing confirmed appointment. Clear tentative time when a slot race returns; tool/ server revalidates on resumed scheduling.
