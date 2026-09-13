# Phase C.1 business-rule update

Source type: **INTERNAL BUSINESS RULE**. Authority: **CTO / Best Driving School business confirmation**. Status: **BUSINESS VERIFIED**. These are internal scheduling rules, not DPS/TDLR regulations or scraped facts.

Standard driving lessons are 120 minutes; divide known purchased driving minutes into full sessions plus a final shorter remainder. Five adult packages map to 1–5 sessions. Both teen packages have 7 actual driving hours: `[120,120,120,60]`, four driving sessions. Classroom and observation scheduling remain separate and unverified. PTDE practice-hour labels and road-test preparation do not establish instructor driving hours, so no lesson plan is inferred for them.

Road tests: 20 minutes service + 5 minutes rollback/reset + 5 minutes system buffer = 30-minute allocation interval. The CTO rule governs intended operational design. Original road frontend observations (15-minute ranges with starts 20 minutes apart) remain preserved; they do not prove backend allocation. Never round, fabricate, or silently reinterpret returned live slots to fit this rule. Validate starts against a confirmed backend schedule origin/resource model; until then, use staff assistance for binding selection.

Historical frontend session fields/evidence are preserved separately from `derived_driving_session_requirement`. Backend enforcement remains independently unverified for every package. Stable package/slot/location/resource IDs, transaction lifecycle, lookup/reschedule/cancel, customer verification, payment/refund policies, pickup/dropoff and remaining-session accounting are still unresolved. No Retell configuration or production capabilities changed.

## Reconciliation coverage

Seven driving package plans derived (five adult, two teen); two road-test packages receive the service allocation model. Three PTDE plans remain unassigned and online education has no timed lesson plan. Original four structured files archived under `data/operational_evidence/phase_c_original/`; original website evidence and regulatory files preserved.

Rebuild safely: `python -m src.manual_retell.business_rules` after any Phase C regeneration. This command is offline and idempotent.

## Validation results

62/62 automated tests pass (50 previous, 12 new). Covers arithmetic/remainder, road allocation, business/regulatory attribution and preservation, all-package plan consistency, historical frontend retention, valid node/variable/handoff references, no static availability and explicit correct-environment confirmation gates. Negative tests reject invalid handoffs, undefined variables, static slots, direct selected-slot confirmation and mock-as-production success. Tests run offline; zero voice calls executed. `git diff --check` passes.
