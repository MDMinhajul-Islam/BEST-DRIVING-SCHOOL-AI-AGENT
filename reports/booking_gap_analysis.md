# Booking gap analysis

Investigation date: 2026-09-13. Frontend observations, public date/time reads and backend-authoritative facts are distinguished. No private account or write workflow was traversed.

| Capability | Status | Gap |
| --- | --- | --- |
| package identification | PARTIALLY VERIFIED | Frontend product IDs; stable database mapping unknown |
| location identification | REQUIRES HUMAN CONFIRMATION | One advertised Plano site; all IDs/resource scopes unknown |
| availability lookup | PARTIALLY VERIFIED | Three GET paths/time-only arrays; no stable slot/resource IDs or timezone |
| session duration | PARTIALLY VERIFIED | Five adult frontend products: two-hour sessions |
| multi-session behavior | PARTIALLY VERIFIED | Adult row count/clearing shown; backend persistence unknown |
| booking creation | REQUIRES BUSINESS ACCESS | Payment form action is not a verified create API |
| booking lookup | NOT FOUND | No endpoint or verified identity mechanism |
| rescheduling | MOCK REQUIRED | School capability unknown |
| cancellation | MOCK REQUIRED | Production human escalation; refund rules unknown |
| payment relationship | PARTIALLY VERIFIED | Pre-submit dates versus pay-then-pick marketing ambiguity |
| processing fees | PARTIALLY VERIFIED | Public 3%; actual checkout calculation unknown |
| pickup/dropoff | REQUIRES HUMAN CONFIRMATION | Address is not pickup proof |
| student verification | REQUIRES BUSINESS ACCESS | Actual reference/authentication rules unknown |

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

Next: obtain official backend contracts and a synthetic sandbox. Confirm product IDs/location/resource mapping, multi-session accounting and transactional success semantics, then implement writes in a separate approved phase. Credentials must be configured only after the actual authentication scheme is known. No guessed credential keys or API paths were added.

## Phase C.1 — CTO business-rule reconciliation

Source type: **INTERNAL BUSINESS RULE**. Authority: **CTO / Best Driving School business confirmation**. Status: **BUSINESS VERIFIED**. These are internal scheduling rules, not DPS/TDLR regulations or scraped facts.

Standard driving lessons are 120 minutes; divide known purchased driving minutes into full sessions plus a final shorter remainder. Five adult packages map to 1–5 sessions. Both teen packages have 7 actual driving hours: `[120,120,120,60]`, four driving sessions. Classroom and observation scheduling remain separate and unverified. PTDE practice-hour labels and road-test preparation do not establish instructor driving hours, so no lesson plan is inferred for them.

Road tests: 20 minutes service + 5 minutes rollback/reset + 5 minutes system buffer = 30-minute allocation interval. The CTO rule governs intended operational design. Original road frontend observations (15-minute ranges with starts 20 minutes apart) remain preserved; they do not prove backend allocation. Never round, fabricate, or silently reinterpret returned live slots to fit this rule. Validate starts against a confirmed backend schedule origin/resource model; until then, use staff assistance for binding selection.

Historical frontend session fields/evidence are preserved separately from `derived_driving_session_requirement`. Backend enforcement remains independently unverified for every package. Stable package/slot/location/resource IDs, transaction lifecycle, lookup/reschedule/cancel, customer verification, payment/refund policies, pickup/dropoff and remaining-session accounting are still unresolved. No Retell configuration or production capabilities changed.
