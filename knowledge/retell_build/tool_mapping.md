# Tool mapping — current capability and manual wiring

Only Booking receives the five logical booking tools. Nodes 01–08 may receive built-in Extract Dynamic Variable for their allowed conversational fields; that is state extraction, not a booking/account/security tool. No production connection is created by this packet.

| Logical tool | Demo local | Production | Wire now? |
| --- | --- | --- | --- |
| check_availability | DEMO AVAILABLE — MockBookingAdapter | PRODUCTION READ AVAILABLE — local BestDrivingSchoolBookingAdapter, explicitly approved enablement only | No hosted wrapper currently deployed |
| create_booking | DEMO AVAILABLE — synthetic only | PRODUCTION WRITE BLOCKED | After approved synthetic wrapper exists, demo only |
| find_booking | DEMO AVAILABLE — verified synthetic fixture | FUTURE — production lookup unavailable | Demo wrapper only, no private enumeration |
| reschedule_booking | DEMO AVAILABLE — version checked, atomic fixture replacement | PRODUCTION WRITE BLOCKED | Demo wrapper only |
| cancel_booking | DEMO AVAILABLE — synthetic release/status, no refund | PRODUCTION WRITE BLOCKED | Demo wrapper only |

## Minimal model-facing arguments and server injection

check_availability: canonical package_id, ISO preferred_date; current live location_id must be null. create_booking: canonical package_id and returned slot_ids after clear caller approval. find_booking: known caller booking reference. reschedule_booking: known reference and returned replacement slot_ids. cancel_booking: known reference and clear caller approval. These are normalized wrapper plans, not native school routes. Existing Python signatures remain in docs/retell_booking_tool_contracts.md; wrapper injects customer_ref, verification_token, idempotency_key and expected_version. Never let the voice model manage those secrets/control keys. No URL is guessed or supplied here.

Manual HTTP wiring requires an approved deployed wrapper URL, authenticated server configuration and response schema tested against the local adapters. Current readiness: local five-operation demo exists; live reads exist default-disabled; Retell HTTP wiring is not ready because wrapper absent. Do not attach a Python path as a URL or native payment form as a booking tool. Booking’s production-safe no-tool fallback is fully usable now.

## Response binding

Use normalized local result success/mode/booking_confirmed and safe error fields. available_slots comes only from check results; selected_slot is a returned caller-selected object, not a manufactured ID. For demo appointment_id maps from booking.appointment_id, active status from booking.booking_status, after explicit correct-mode success; cancelled status never implies active confirmation. A wrapper must expose known session count/plan and sanitized per-session progress before binding those derived display fields. No raw body/trace or verification secret exposed. Backend owns multi-session accumulated selections, idempotency/version/race and reconciliation. Current mock one-hour fixtures do not establish real lesson duration or school accounting; faithful multi-session demo needs duration-aware fixtures.

## Mode setup and confirmation gate

Default global prompt begins Build mode: PRODUCTION-SAFE. For an isolated synthetic test, human builder replaces that first line with exactly: Build mode: DEMO. All appointments are synthetic test records; never confirm a real school reservation. Match wrapper permissions to the chosen configuration. Caller cannot change modes. Omit all production writes and lookup. Real confirmation needs authorized correct-environment explicit backend success, booking_confirmed=true and appointment ID; current production permission is false. Mock success is always described as demo. Read failure retry at most once; write timeout stays outcome unknown and goes to staff/reconciliation without a blind repeat.
