# Future booking tool contracts

Design date: 2026-09-13. OUR NORMALIZED INTERFACE — not a claim about school endpoints or a Retell import.

All responses include `success`, `mode` and `booking_confirmed`. Errors include safe `error_code`/`user_safe_message`; no internal traces or customer/session secrets. `mode=mock` additionally marks synthetic=true, production=false.

| Operation | Our required inputs | Optional/conditional | Server-generated output | School contract status |
| --- | --- | --- | --- | --- |
| check_availability | package_id, preferred_date | location_id only once authoritative mapping exists; currently null in live | normalized time labels; real slot ID unavailable | Three date-only GET time routes evidenced |
| create_booking | package_id, selected slot_ids, verified customer_ref, verification_token, idempotency_key | Multiple slots according to approved package rules; contact/enrollment fields later require explicit policy | appointment_id, booking_status, version | UNKNOWN; synthetic mock only |
| find_booking | appointment_id, verified customer_ref, verification_token | Phone/email lookup only if approved non-enumerating verification contract is later documented | Verified minimal booking summary | UNKNOWN; synthetic mock only |
| reschedule_booking | appointment_id, selected slot_ids, verified customer_ref, verification_token, expected_version | Apply confirmed business cutoff/session rules | Updated booking/version | UNKNOWN; synthetic mock only |
| cancel_booking | appointment_id, verified customer_ref, verification_token, expected_version | Apply approved cancellation authorization; refund is separate | Cancelled status/version | UNKNOWN; synthetic mock only |

Customer_ref/verification_token are our proposed verified-session references, not claims that the school API has those fields. In mock they must be the pre-provisioned MOCK-CUSTOMER/VERIFY fixtures; no real names/contact/DOB records are accepted by the mock interface. Actual public payment form names are preserved separately without values; they are NOT implemented as a create API. Required-versus-optional backend field validation is unknown beyond native frontend attributes.

Retry creation with the same idempotency key; mismatched payload yields IDEMPOTENCY_CONFLICT. Real school idempotency support is unknown: an adapter must implement durable deduplication and reconcile uncertain outcomes rather than blindly retrying. Reschedule checks replacement capacity before releasing old slots. A slot race returns SLOT_NO_LONGER_AVAILABLE, refreshes availability and asks for a new selection. Timeout on a future write means outcome unknown; never claim failure is proof that no booking exists.

Payment-card collection is outside these contracts. Secure checkout URLs, payment confirmation, fee rounding and temporary holds require an approved contract. No production custom function was created.

## Phase C.1 — CTO business-rule reconciliation

Source type: **INTERNAL BUSINESS RULE**. Authority: **CTO / Best Driving School business confirmation**. Status: **BUSINESS VERIFIED**. These are internal scheduling rules, not DPS/TDLR regulations or scraped facts.

Standard driving lessons are 120 minutes; divide known purchased driving minutes into full sessions plus a final shorter remainder. Five adult packages map to 1–5 sessions. Both teen packages have 7 actual driving hours: `[120,120,120,60]`, four driving sessions. Classroom and observation scheduling remain separate and unverified. PTDE practice-hour labels and road-test preparation do not establish instructor driving hours, so no lesson plan is inferred for them.

Road tests: 20 minutes service + 5 minutes rollback/reset + 5 minutes system buffer = 30-minute allocation interval. The CTO rule governs intended operational design. Original road frontend observations (15-minute ranges with starts 20 minutes apart) remain preserved; they do not prove backend allocation. Never round, fabricate, or silently reinterpret returned live slots to fit this rule. Validate starts against a confirmed backend schedule origin/resource model; until then, use staff assistance for binding selection.

Historical frontend session fields/evidence are preserved separately from `derived_driving_session_requirement`. Backend enforcement remains independently unverified for every package. Stable package/slot/location/resource IDs, transaction lifecycle, lookup/reschedule/cancel, customer verification, payment/refund policies, pickup/dropoff and remaining-session accounting are still unresolved. No Retell configuration or production capabilities changed.
