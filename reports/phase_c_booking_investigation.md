# Phase C booking investigation

Investigation date: 2026-09-13. Frontend observations, public date/time reads and backend-authoritative facts are distinguished. No private account or write workflow was traversed.

Thirteen packages remain intact; 12 use scheduling. All 12 schedulable options have observed form product_id values, but 0/12 have independently verified stable backend identifiers. Three date-based GET availability paths are confirmed in frontend code and read successfully without authentication (road: 27 time labels; adult: empty; teen: five on one date). Five adult products control one–five two-hour appointment rows. No production booking, lookup, reschedule, cancellation or payment transaction was performed. A disabled-by-default read-only adapter and a synthetic mock provide separate capabilities.

| Package | Schedulable? | Backend ID known? | Location known? | Session model known? | Availability method known? | Booking method known? | Production ready? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 24 Hr Classroom + Driving Package | True | Form product 1; backend stability unverified | IDs unknown; Plano school/service areas advertised | Partial/unknown | /api/teen-appointment-times | Payment form only; booking creation unverified | NO |
| Behind the Wheel Only (7 & 7) | True | Form product 3; backend stability unverified | IDs unknown; Plano school/service areas advertised | Partial/unknown | /api/teen-appointment-times | Payment form only; booking creation unverified | NO |
| 10 hours | True | Form product 8; backend stability unverified | IDs unknown; Plano school/service areas advertised | Partial/unknown | /api/teen-appointment-times | Payment form only; booking creation unverified | NO |
| 15 hours | True | Form product 7; backend stability unverified | IDs unknown; Plano school/service areas advertised | Partial/unknown | /api/teen-appointment-times | Payment form only; booking creation unverified | NO |
| 30 hours | True | Form product 6; backend stability unverified | IDs unknown; Plano school/service areas advertised | Partial/unknown | /api/teen-appointment-times | Payment form only; booking creation unverified | NO |
| 6-Hour Online Permit Class | False | Form product unknown; backend stability unverified | IDs unknown; Plano school/service areas advertised | Partial/unknown | No timed form | Payment form only; booking creation unverified | NO |
| Road test only | True | Form product 4; backend stability unverified | IDs unknown; Plano school/service areas advertised | Partial/unknown | /api/appointment-times | Payment form only; booking creation unverified | NO |
| Practice session + road test | True | Form product 5; backend stability unverified | IDs unknown; Plano school/service areas advertised | Partial/unknown | /api/appointment-times | Payment form only; booking creation unverified | NO |
| 2 hours | True | Form product 10; backend stability unverified | IDs unknown; Plano school/service areas advertised | Adult two-hour rows (frontend) | /api/adult-appointment-times | Payment form only; booking creation unverified | NO |
| 4 hours | True | Form product 11; backend stability unverified | IDs unknown; Plano school/service areas advertised | Adult two-hour rows (frontend) | /api/adult-appointment-times | Payment form only; booking creation unverified | NO |
| 6 hours | True | Form product 12; backend stability unverified | IDs unknown; Plano school/service areas advertised | Adult two-hour rows (frontend) | /api/adult-appointment-times | Payment form only; booking creation unverified | NO |
| 8 hours | True | Form product 13; backend stability unverified | IDs unknown; Plano school/service areas advertised | Adult two-hour rows (frontend) | /api/adult-appointment-times | Payment form only; booking creation unverified | NO |
| 10 hours | True | Form product 14; backend stability unverified | IDs unknown; Plano school/service areas advertised | Adult two-hour rows (frontend) | /api/adult-appointment-times | Payment form only; booking creation unverified | NO |

## Package Mapping

Observed product_id values: teen full 1, teen BTW 3, road only 4, practice/test 5, PTDE 10h 8/15h 7/30h 6, adult 2–10h 10–14. Online analytics item_id 15 is not a verified purchase identifier. Course/service/schedule IDs and location-dependent identity are unknown. See package_backend_map.json.

## Location Mapping

One public school/testing location in Plano is advertised. Allen, Frisco and McKinney are service areas; no internal location IDs or location selector appears in the inspected forms/availability requests. Operational locations independently verified: zero. Do not create four branches in the adapter.

## Session Model

Adult five variants collect one–five rows and the live form explicitly states each session is two hours. Switching from two to four hours reveals a second row. Date changes clear subsequent rows and constrain the next date at least one day later in frontend JS. Backend enforcement, independent remaining-session booking and tracking remain unknown. PTDE all three products carry data-blocks=7, but saved forms expose no matching appointment rows; never equate these with purchased 10/15/30 hours. Teen full uses class_code for a classroom cohort; in-car/observation scheduling is unverified.

## Availability

Observed routes: GET /api/appointment-times, /api/adult-appointment-times, /api/teen-appointment-times with date only; Accept application/json and no-store in JS. Anonymous read replays returned HTTP 200 arrays. JS also accepts object values. No product, location, examiner, vehicle or customer parameter is sent by this frontend flow. Dates/time labels are ephemeral observations, not static capacity guarantees. Timezone, stable slot IDs and resource meaning are unknown. Road ranges observed were 15 minutes; this is not proof of total test/practice service duration.

## Booking

The form declares POST https://bestdrivingschool.us/product/index/payment. It collects enrollment/contact details and appointment selections before Submit, with a notice that payment/total review is on the next screen. No POST was sent; whether it creates an enrollment, provisional hold or booking is unknown. Production write adapter methods are hard-disabled.

## Lookup

UNKNOWN — ENDPOINT NOT YET CONFIRMED. No booking/customer enumeration. Proposed normalized lookup is limited to a verified customer and a known appointment reference; actual school verification/reference mechanisms require authorized access.

## Reschedule

UNKNOWN — ENDPOINT NOT YET CONFIRMED. Proposed safe flow: verified lookup → availability → customer selection → atomic reschedule with version checks → explicit backend success. Only mock implements this; school support/cutoffs are unknown.

## Cancellation

UNKNOWN — ENDPOINT NOT YET CONFIRMED. HUMAN ESCALATION REQUIRED for production. No refund or cancellation cutoff inferred from the 3% non-refundable processing charge. Mock cancellation releases synthetic slots and changes mock status only.

## Payment

PARTIAL: dates may be selected in the public road/adult form before the declared payment POST, but adult marketing says pay then pick times. Preserve the sequence ambiguity. Checkout/payment/access activation/temporary reservations/webhooks remain unknown. Online education has no local form and an external access link; enrollment/account activation was not observed. No card data handled.

## Fees

Public pages advertise a separate 3% non-refundable online processing charge. No checkout was submitted and no final-total calculation, tax, deposit or rounding rule was observed. Do not report base×1.03 as a confirmed payable total.

## Pickup / Dropoff

Street address fields are contact/address collection, not proof of pickup. No pickup-specific selector, coverage radius or fee was verified. Package-specific pickup/dropoff requires owner confirmation; see pickup_dropoff_findings.md.

## Security

Public read-only date/time endpoints were accessed without tokens or cookies intentionally supplied. F12 did not expose a raw network panel through the available browser control; endpoint/status/body shape are evidenced by frontend JS plus one read replay per route, not falsely labeled as captured DevTools traffic. No authentication/CSRF bypass. Logs retain field names and time labels only, never session/customer/driver/payment values.

## Missing Access

Application routes/controllers/database schema, approved backend documentation/sandbox, customer-verification mechanism, transaction lifecycle, appointment identity, resource allocation, cancellations/refunds and checkout totals are unavailable in this repository. Owner-provided documentation or a synthetic sandbox account is needed for safe write-flow investigation.

## Retell Readiness

Common interface specs and failure/state rules are ready for manual planning. Live adapter performs only evidenced GET availability and cannot create/find/change bookings. Default live disabled; enable explicitly via constructor only for approved read-only use. Mock supports synthetic create/find/reschedule/cancel with verification, slot races, atomic replacement and idempotency. Nothing is configured in Retell. Production custom functions are not ready until identifier, verification and transactional gaps close.


## Validation

50/50 tests pass (36 existing and 14 new), including preservation hashes and booking safety cases. Offline synthetic demo exercises all five operations; see phase_c_mock_demo.json and phase_c_test_results.md. Five adult session models are evidenced at the frontend only; zero backend-enforced session models verified. Four adult multi-session package row models are understood at the frontend; backend scheduling rules remain unresolved for all 12 schedulable packages.

## Phase C.1 — CTO business-rule reconciliation

Source type: **INTERNAL BUSINESS RULE**. Authority: **CTO / Best Driving School business confirmation**. Status: **BUSINESS VERIFIED**. These are internal scheduling rules, not DPS/TDLR regulations or scraped facts.

Standard driving lessons are 120 minutes; divide known purchased driving minutes into full sessions plus a final shorter remainder. Five adult packages map to 1–5 sessions. Both teen packages have 7 actual driving hours: `[120,120,120,60]`, four driving sessions. Classroom and observation scheduling remain separate and unverified. PTDE practice-hour labels and road-test preparation do not establish instructor driving hours, so no lesson plan is inferred for them.

Road tests: 20 minutes service + 5 minutes rollback/reset + 5 minutes system buffer = 30-minute allocation interval. The CTO rule governs intended operational design. Original road frontend observations (15-minute ranges with starts 20 minutes apart) remain preserved; they do not prove backend allocation. Never round, fabricate, or silently reinterpret returned live slots to fit this rule. Validate starts against a confirmed backend schedule origin/resource model; until then, use staff assistance for binding selection.

Historical frontend session fields/evidence are preserved separately from `derived_driving_session_requirement`. Backend enforcement remains independently unverified for every package. Stable package/slot/location/resource IDs, transaction lifecycle, lookup/reschedule/cancel, customer verification, payment/refund policies, pickup/dropoff and remaining-session accounting are still unresolved. No Retell configuration or production capabilities changed.
