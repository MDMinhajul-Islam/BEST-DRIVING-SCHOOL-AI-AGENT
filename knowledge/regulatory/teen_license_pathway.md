# Teen License Pathway

Regulatory research date: 2026-09-13

General Class C guidance. Use only records marked `official_verified` for general answers; flagged details require confirmation. Source dates are not assumed effective dates.

## TX-R005: Start education at 14, learner at 15

Applies when: `{"age_max": 17, "first_license": true}`

- Classroom education may begin at 14; a learner license requires age 15 or older.

Confidence: `official_verified`. Review required: False.

Sources: [TX-TDLR-001](https://www.tdlr.texas.gov/driver/education/students/do-i-need-driver-ed/), [TX-TDLR-005](https://www.tdlr.texas.gov/driver/education/parent-taught/learner-license.htm)

## TX-R014: In-car instruction and practice are separate

Applies when: `{"teen_course": true}`

- Complete seven hours driving instruction, seven observation hours, and 30 additional supervised practice hours including ten at night. A school package is not automatically all 44 hours.

Confidence: `official_verified`. Review required: False.

Sources: [TX-TDLR-002](https://www.tdlr.texas.gov/driver/education/parent-taught/), [TX-TDLR-P03](https://www.tdlr.texas.gov/media/pdf/DES-at-a-glance.pdf)

## TX-R015: Practice supervision and log

Applies when: `{"teen_course": true, "practice_hours": true}`

- The practice supervisor must be 21+, licensed for at least a year; the parent/guardian certifies the 30-hour practice log. Follow the approved course instructions for other logs.

Confidence: `official_verified`. Review required: False.

Sources: [TX-TDLR-006](https://www.tdlr.texas.gov/driver/education/parent-taught/behind-the-wheel.htm)

## TX-R017: Provisional passenger and nighttime restrictions

Applies when: `{"age_max": 17, "provisional_license": true}`

- No more than one non-family passenger under 21. No driving midnight–5 a.m. except work, school activities or emergencies.

Confidence: `official_verified`. Review required: False.

Sources: [TX-TDLR-007](https://www.tdlr.texas.gov/driver/education/parent-taught/provisional-license.htm), [TX-DPS-004](https://www.dps.texas.gov/section/driver-license/graduated-driver-license-gdl-and-hardship-license)

## TX-R018: Device restriction

Applies when: `{"age_max": 17, "learner_or_provisional": true}`

- Cellphone use, including hands-free, is prohibited while driving except an emergency under the cited teen guidance.

Confidence: `official_verified`. Review required: False.

Sources: [TX-DPS-002](https://www.dps.texas.gov/section/driver-license/texas-learners-license-teen), [TX-TDLR-007](https://www.tdlr.texas.gov/driver/education/parent-taught/provisional-license.htm)

## TX-R056: Provisional expiry versus restrictions

Applies when: `{"provisional_license": true, "age_transition": 18}`

- TDLR's step guide says the provisional license expires at 18 and must be renewed. Confirm the exact expiry of each restriction with DPS; turning 18 does not itself renew an expired document.

Confidence: `requires_dps_confirmation`. Review required: True.

Sources: [TX-TDLR-P01](https://www.tdlr.texas.gov/driver/docs/parent-taught-step-by-step-guide.pdf)

