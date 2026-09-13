# Booking persona data requirements

Manual planning only. Receive intent, program/course/canonical package ID/name, sourced package price, school/regulatory prerequisite status, preferred location/date/time and selected returned slot. Do not confuse canonical IDs with provisional public form product IDs. Location IDs and stable live slot IDs are not confirmed.

Ask only necessary unanswered preferences. Student/caller name and phone/email are caller-provided inputs if later required; verified customer_ref and appointment_id must come from an approved backend. DOB/permit numbers and payment-card information should remain in secure official enrollment/checkout flows. Actual verification and required fields need business approval. Multi-session choices may require several appointments; frontend row count alone is not confirmed remaining-hours accounting.

Proposed operational variables: location_id/location_name, selected_slot_id, verified_customer_ref, verification_status, appointment_id, booking_status, booking_version, adapter_mode and last_tool_result. Preserve existing program/course/package/price and caller preference proposals. No Retell variables or workflow nodes were configured. Mock results are for testing only and must be identified as mock in every answer.

## Phase C.1 — CTO business-rule reconciliation

Source type: **INTERNAL BUSINESS RULE**. Authority: **CTO / Best Driving School business confirmation**. Status: **BUSINESS VERIFIED**. These are internal scheduling rules, not DPS/TDLR regulations or scraped facts.

Standard driving lessons are 120 minutes; divide known purchased driving minutes into full sessions plus a final shorter remainder. Five adult packages map to 1–5 sessions. Both teen packages have 7 actual driving hours: `[120,120,120,60]`, four driving sessions. Classroom and observation scheduling remain separate and unverified. PTDE practice-hour labels and road-test preparation do not establish instructor driving hours, so no lesson plan is inferred for them.

Road tests: 20 minutes service + 5 minutes rollback/reset + 5 minutes system buffer = 30-minute allocation interval. The CTO rule governs intended operational design. Original road frontend observations (15-minute ranges with starts 20 minutes apart) remain preserved; they do not prove backend allocation. Never round, fabricate, or silently reinterpret returned live slots to fit this rule. Validate starts against a confirmed backend schedule origin/resource model; until then, use staff assistance for binding selection.

Historical frontend session fields/evidence are preserved separately from `derived_driving_session_requirement`. Backend enforcement remains independently unverified for every package. Stable package/slot/location/resource IDs, transaction lifecycle, lookup/reschedule/cancel, customer verification, payment/refund policies, pickup/dropoff and remaining-session accounting are still unresolved. No Retell configuration or production capabilities changed.
