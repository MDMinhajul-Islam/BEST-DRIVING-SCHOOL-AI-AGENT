# Booking state reference

`availability_checked` → `slot_selected` → `booking_pending` → `booking_confirmed` only after explicit backend success and a returned appointment identifier. Any negative/uncertain result stays `booking_failed` or pending reconciliation; never say “You’re booked” from a selected slot, a submitted request or a timeout. Availability reads always report booking_confirmed=false. Mock success must be described as a mock reservation only.

Slot race: return SLOT_NO_LONGER_AVAILABLE → refresh availability → offer new returned slots → customer selects again. Retry creation with the same idempotency key; real school idempotency is unverified. For reschedule, verify known booking/customer, check new slots, receive selection and update atomically before confirmation. Cancellation requires approved policy and verification; refunds are not implied. Production cancellation currently requires human escalation.

Normalized errors: TIMEOUT, INVALID_PACKAGE, INVALID_LOCATION, SLOT_NO_LONGER_AVAILABLE, BACKEND_UNAVAILABLE, AUTHENTICATION_FAILURE, VALIDATION_ERROR, UNKNOWN_SERVER_ERROR, IDEMPOTENCY_CONFLICT, LIVE_DISABLED and LIVE_WRITES_DISABLED. Provide safe messages without internal details. These are our interface semantics, not observed school error enums.

## Phase C.1 — CTO business-rule reconciliation

Source type: **INTERNAL BUSINESS RULE**. Authority: **CTO / Best Driving School business confirmation**. Status: **BUSINESS VERIFIED**. These are internal scheduling rules, not DPS/TDLR regulations or scraped facts.

Standard driving lessons are 120 minutes; divide known purchased driving minutes into full sessions plus a final shorter remainder. Five adult packages map to 1–5 sessions. Both teen packages have 7 actual driving hours: `[120,120,120,60]`, four driving sessions. Classroom and observation scheduling remain separate and unverified. PTDE practice-hour labels and road-test preparation do not establish instructor driving hours, so no lesson plan is inferred for them.

Road tests: 20 minutes service + 5 minutes rollback/reset + 5 minutes system buffer = 30-minute allocation interval. The CTO rule governs intended operational design. Original road frontend observations (15-minute ranges with starts 20 minutes apart) remain preserved; they do not prove backend allocation. Never round, fabricate, or silently reinterpret returned live slots to fit this rule. Validate starts against a confirmed backend schedule origin/resource model; until then, use staff assistance for binding selection.

Historical frontend session fields/evidence are preserved separately from `derived_driving_session_requirement`. Backend enforcement remains independently unverified for every package. Stable package/slot/location/resource IDs, transaction lifecycle, lookup/reschedule/cancel, customer verification, payment/refund policies, pickup/dropoff and remaining-session accounting are still unresolved. No Retell configuration or production capabilities changed.
