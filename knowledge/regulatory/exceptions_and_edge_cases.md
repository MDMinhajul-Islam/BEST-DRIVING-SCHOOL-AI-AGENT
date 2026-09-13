# Exceptions And Edge Cases

Regulatory research date: 2026-09-13

General Class C guidance. Use only records marked `official_verified` for general answers; flagged details require confirmation. Source dates are not assumed effective dates.

## TX-R037: Residency affidavit option

Applies when: `{"cannot_supply_two_residency_documents": true}`

- DPS provides a conditional residency-affidavit option and special cases. Confirm the appropriate affidavit and supporting documentation with DPS; it is not a blanket exemption.

Confidence: `requires_dps_confirmation`. Review required: True.

Sources: [TX-DPS-010](https://www.dps.texas.gov/section/driver-license/texas-residency-requirement-driver-licenses-and-id-cards)

## TX-R039: SSN ineligibility affidavit

Applies when: `{"ssn_eligible": false}`

- DPS describes an office SSN affidavit for ineligible applicants. The page's never-applied/applied-and-denied wording is ambiguous; have DPS confirm eligibility and required evidence.

Confidence: `requires_dps_confirmation`. Review required: True.

Sources: [TX-DPS-011](https://www.dps.texas.gov/section/driver-license/social-security-number-ssn)

## TX-R053: Hardship license exception

Applies when: `{"age_min": 15, "age_max": 17, "hardship_claimed": true}`

- DPS describes a necessity-based minor restricted/hardship license with an exception to the six-month learner hold and expiry at the next birthday. DPS must establish the qualifying hardship; do not infer approval.

Confidence: `requires_dps_confirmation`. Review required: True.

Sources: [TX-DPS-004](https://www.dps.texas.gov/section/driver-license/graduated-driver-license-gdl-and-hardship-license)

## TX-R054: Military/NATO exceptions

Applies when: `{"military_or_nato_claimed": true}`

- DPS describes conditional military-extension and NATO-order testing exemptions. Route documentation and applicability to DPS rather than promising a waiver.

Confidence: `requires_dps_confirmation`. Review required: True.

Sources: [TX-DPS-007](https://www.dps.texas.gov/section/driver-license/moving-texas-guide-driver-licenses-and-ids)

