# Driver Education Requirements

Regulatory research date: 2026-09-13

General Class C guidance. Use only records marked `official_verified` for general answers; flagged details require confirmation. Source dates are not assumed effective dates.

## TX-R006: Teen classroom total has conflicting official wording

Applies when: `{"age_max": 17, "teen_course": true}`

- Current overview pages and ITTD FAQ describe 24 classroom hours; TDLR learner/block and hybrid pages still say 32. Do not quote one universal total or completion schedule until TDLR/provider review.

Confidence: `conflicting_official_sources`. Review required: True.

Sources: [TX-TDLR-001](https://www.tdlr.texas.gov/driver/education/students/do-i-need-driver-ed/), [TX-TDLR-005](https://www.tdlr.texas.gov/driver/education/parent-taught/learner-license.htm), [TX-TDLR-008](https://www.tdlr.texas.gov/driver/education/parent-taught/hybrid-instruction.htm), [TX-DPS-016](https://impacttexasdrivers.dps.texas.gov/ittd/FAQ.aspx)

## TX-R027: Approved education options

Applies when: `{"driver_education_required": true}`

- Use an approved driver education provider, an eligible public-school course or authorized PTDE pathway. Confirm the provider's relevant approval/endorsement before choosing an online or parent-taught course.

Confidence: `official_verified`. Review required: False.

Sources: [TX-TDLR-001](https://www.tdlr.texas.gov/driver/education/students/do-i-need-driver-ed/), [TX-TDLR-004](https://www.tdlr.texas.gov/driver/education/parent-taught/classroom-instruction.htm)

## TX-R028: Turning 18 during teen education

Applies when: `{"age_min": 18, "partial_teen_course": true}`

- Partial teen classroom hours cannot be credited toward the six-hour adult course. Complete the full teen program or full adult course.

Confidence: `official_verified`. Review required: False.

Sources: [TX-TDLR-009](https://www.tdlr.texas.gov/driver/education/students/faq.htm)

## TX-R029: Education transfers and duplicate certificates

Applies when: `{"education_transfer_or_duplicate": true}`

- Contact the original approved provider for duplicate certificates. Texas-licensed school transfers are possible; out-of-state education hours do not transfer under TDLR guidance—confirm the licensing scenario with DPS.

Confidence: `official_verified`. Review required: False.

Sources: [TX-TDLR-009](https://www.tdlr.texas.gov/driver/education/students/faq.htm)

