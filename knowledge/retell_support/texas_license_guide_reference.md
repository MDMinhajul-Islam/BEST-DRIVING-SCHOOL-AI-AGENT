# Texas License Guide reference

Regulatory research date: 2026-09-13

Internal reference for manual node design; not a final prompt or workflow import.

## What we need to know from the caller

Age of student, first/existing license, exact credential and jurisdiction, residency/move date, education/certificate status, learner issue date when relevant, PTDE designation and testing goal. For tests, establish ITD program/date and unresolved prerequisites. Reuse known answers.

## Possible pathways and rules

| Pathway | General guidance readiness | Rule IDs |
| --- | --- | --- |
| teen_first_time | REVIEW | TX-R005, TX-R006, TX-R007, TX-R013, TX-R009, TX-R010, TX-R014, TX-R015, TX-R016, TX-R017, TX-R018 |
| adult_first_time_18_24 | READY | TX-R001, TX-R003, TX-R034, TX-R030, TX-R031, TX-R032, TX-R004 |
| adult_first_time_25_plus | READY | TX-R002, TX-R003, TX-R034, TX-R030, TX-R031, TX-R032, TX-R004 |
| adult_with_learner_license | REVIEW | TX-R055, TX-R001, TX-R002, TX-R030, TX-R032, TX-R045 |
| teen_with_learner_license | REVIEW | TX-R010, TX-R014, TX-R015, TX-R016, TX-R006 |
| parent_taught_student | REVIEW | TX-R021, TX-R022, TX-R023, TX-R019, TX-R020, TX-R007, TX-R008, TX-R024, TX-R014, TX-R015, TX-R025, TX-R016 |
| road_test_ready | REVIEW | TX-R016, TX-R030, TX-R032, TX-R041, TX-R042, TX-R043, TX-R045, TX-R004 |
| new_texas_resident | REVIEW | TX-R046, TX-R034, TX-R036, TX-R047, TX-R048, TX-R049, TX-R050 |
| out_of_state_transfer | READY | TX-R046, TX-R047, TX-R034, TX-R036 |
| foreign_license_holder | REVIEW | TX-R050, TX-R051, TX-R052, TX-R040, TX-R034 |
| uncertain_or_exception | REVIEW | TX-R037, TX-R039, TX-R048, TX-R053, TX-R054, TX-R056 |

## Manual routing reference

Adult Sales: adult education or optional in-car learning needs; do not force education at 25+. Teen Sales: teen education/driving/PTDE component needs. Road Test Sales: skills testing or preparation after clarification; no automatic eligibility guarantee. Booking: only after the reviewed prerequisites and selected service are established; actual availability/actions require a later backend. Human support: disputed rules, provider authorization, unusual documents, transfer/foreign exceptions or caller contradictions.

## Clarification and no-guess cases

Unclear age/student identity, “permit” without exact credential, expired or foreign licenses, partial teen education at 18, adult teen-certificate ITD selection, incomplete PTDE authorization or logs, and uncertain document acceptance. See regulatory unresolved questions. Use only `official_verified` records; blocking a disputed detail does not prevent explaining other supported steps.
