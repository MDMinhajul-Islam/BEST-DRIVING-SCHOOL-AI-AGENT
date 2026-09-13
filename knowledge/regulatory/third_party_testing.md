# Third Party Testing

Regulatory research date: 2026-09-13

General Class C guidance. Use only records marked `official_verified` for general answers; flagged details require confirmation. Source dates are not assumed effective dates.

## TX-R004: Testing versus issuance

Applies when: `{"third_party_test": true}`

- Testing may be completed through an eligible third-party provider. DPS completes license issuance; a test pass alone is not a license.

Confidence: `official_verified`. Review required: False.

Sources: [TX-DPS-001](https://www.dps.texas.gov/section/driver-license/apply-texas-driver-license)

## TX-R044: Teen post-test submission

Applies when: `{"age_max": 17, "third_party_test": true}`

- DL-68 describes submitting third-party results in a sealed unaltered envelope with applicable provisional documents and completed classroom/in-car certificates. Confirm whether the specific approved provider uses an authorized digital process instead.

Confidence: `requires_human_review`. Review required: True.

Sources: [TX-DPS-P02](https://www.dps.texas.gov/Internetforms/Forms/DL-68.pdf)

## TX-R045: Provider-specific testing gate remains unverified

Applies when: `{"third_party_test": true}`

- DPS and TDLR support third-party skills testing generally, but the TPST program page and DL-65 could not be reviewed. Confirm current adult restricted-license prerequisites and the school's active testing authorization before booking.

Confidence: `requires_human_review`. Review required: True.

Sources: [TX-DPS-001](https://www.dps.texas.gov/section/driver-license/apply-texas-driver-license), [TX-TDLR-007](https://www.tdlr.texas.gov/driver/education/parent-taught/provisional-license.htm)

