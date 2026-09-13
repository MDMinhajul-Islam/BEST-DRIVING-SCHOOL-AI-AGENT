# Availability contract

Design date: 2026-09-13. OUR NORMALIZED INTERFACE — not a claim about school endpoints or a Retell import.

Method: `check_availability(package_id, preferred_date, location_id=null)`. Package/date are required by our adapter; the school frontend sends only `date`. Canonical package selects an evidenced route internally. An internal location ID is unconfirmed, so live mode rejects a supplied location_id. Date format is ISO YYYY-MM-DD. No customer data is required for the observed availability read.

Output: success, mode, package_id, available_slots and booking_confirmed=false. Each normalized time has date/start_time/end_time/backend_time_label; slot_id=null, timezone=null, bookable_through_this_adapter=false. Empty array is successful empty availability; malformed/unavailable responses are errors. An object response is interpreted by its values exactly as the frontend does, then sorted/deduplicated. Never fabricate a stable slot ID from the displayed time.

Live route lookup is allowlisted to the three observed time endpoints. No product/location/date-range/resource parameters are guessed. No redirect following or raw internal response exposure. Production creation must wait for authoritative slot/booking identity and timezone confirmation. Mock uses explicit MOCK-SLOT/MOCK-LOCATION fixtures with synthetic times, not those live labels.

## Phase C.1 — CTO business-rule reconciliation

Source type: **INTERNAL BUSINESS RULE**. Authority: **CTO / Best Driving School business confirmation**. Status: **BUSINESS VERIFIED**. These are internal scheduling rules, not DPS/TDLR regulations or scraped facts.

Standard driving lessons are 120 minutes; divide known purchased driving minutes into full sessions plus a final shorter remainder. Five adult packages map to 1–5 sessions. Both teen packages have 7 actual driving hours: `[120,120,120,60]`, four driving sessions. Classroom and observation scheduling remain separate and unverified. PTDE practice-hour labels and road-test preparation do not establish instructor driving hours, so no lesson plan is inferred for them.

Road tests: 20 minutes service + 5 minutes rollback/reset + 5 minutes system buffer = 30-minute allocation interval. The CTO rule governs intended operational design. Original road frontend observations (15-minute ranges with starts 20 minutes apart) remain preserved; they do not prove backend allocation. Never round, fabricate, or silently reinterpret returned live slots to fit this rule. Validate starts against a confirmed backend schedule origin/resource model; until then, use staff assistance for binding selection.

Historical frontend session fields/evidence are preserved separately from `derived_driving_session_requirement`. Backend enforcement remains independently unverified for every package. Stable package/slot/location/resource IDs, transaction lifecycle, lookup/reschedule/cancel, customer verification, payment/refund policies, pickup/dropoff and remaining-session accounting are still unresolved. No Retell configuration or production capabilities changed.
