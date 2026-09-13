# Learner License

Regulatory research date: 2026-09-13

General Class C guidance. Use only records marked `official_verified` for general answers; flagged details require confirmation. Source dates are not assumed effective dates.

## TX-R007: Concurrent learner classroom milestone

Applies when: `{"age_min": 15, "age_max": 17, "method": "concurrent"}`

- Complete the first six classroom hours and obtain the learner-stage education certificate before applying to DPS.

Confidence: `official_verified`. Review required: False.

Sources: [TX-DPS-002](https://www.dps.texas.gov/section/driver-license/texas-learners-license-teen), [TX-TDLR-005](https://www.tdlr.texas.gov/driver/education/parent-taught/learner-license.htm)

## TX-R008: Block learner milestone needs review

Applies when: `{"age_min": 15, "age_max": 17, "method": "block"}`

- Block method completes all classroom instruction before the learner application; the official 24/32-hour discrepancy must be resolved for the selected course.

Confidence: `conflicting_official_sources`. Review required: True.

Sources: [TX-DPS-002](https://www.dps.texas.gov/section/driver-license/texas-learners-license-teen), [TX-TDLR-005](https://www.tdlr.texas.gov/driver/education/parent-taught/learner-license.htm)

## TX-R009: Supervising adult

Applies when: `{"teen_learner_license": true}`

- Drive only with a licensed adult aged at least 21 in the front passenger seat.

Confidence: `official_verified`. Review required: False.

Sources: [TX-DPS-002](https://www.dps.texas.gov/section/driver-license/texas-learners-license-teen), [TX-TDLR-005](https://www.tdlr.texas.gov/driver/education/parent-taught/learner-license.htm)

## TX-R010: Holding period

Applies when: `{"age_max": 17, "texas_learner_license": true, "hardship_exception": false}`

- Hold the learner license at least six months unless turning 18 first. Suspension extends the holding period by the suspension duration.

Confidence: `official_verified`. Review required: False.

Sources: [TX-DPS-002](https://www.dps.texas.gov/section/driver-license/texas-learners-license-teen), [TX-DPS-004](https://www.dps.texas.gov/section/driver-license/graduated-driver-license-gdl-and-hardship-license)

## TX-R011: Learner validity

Applies when: `{"teen_learner_license": true}`

- The teen learner license expires on the 18th birthday; confirm the next DPS application rather than assuming automatic conversion.

Confidence: `official_verified`. Review required: False.

Sources: [TX-DPS-002](https://www.dps.texas.gov/section/driver-license/texas-learners-license-teen)

## TX-R055: Adult permit and waiting-period gap

Applies when: `{"age_min": 18, "adult_learner_or_restricted_license": true}`

- The six-month holding rule is verified for minors, not automatically adults. Exact adult restricted-license acquisition and third-party test prerequisites remain unverified in this snapshot; confirm with DPS/provider.

Confidence: `requires_human_review`. Review required: True.

Sources: [TX-DPS-002](https://www.dps.texas.gov/section/driver-license/texas-learners-license-teen), [TX-DPS-001](https://www.dps.texas.gov/section/driver-license/apply-texas-driver-license)


Official term: **Learner License**. Caller aliases: permit, learner permit, instruction permit. These aliases help recognize intent; they do not establish an equivalent credential or extend teen rules to adults.
