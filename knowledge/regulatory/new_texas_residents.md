# New Texas Residents

Regulatory research date: 2026-09-13

General Class C guidance. Use only records marked `official_verified` for general answers; flagged details require confirmation. Source dates are not assumed effective dates.

## TX-R046: Resident driving deadline

Applies when: `{"new_texas_resident": true, "valid_recognized_license": true}`

- DPS permits driving with a valid unexpired US-state/territory, Canadian or qualifying-country license for up to 90 days after moving to Texas.

Confidence: `official_verified`. Review required: False.

Sources: [TX-DPS-007](https://www.dps.texas.gov/section/driver-license/moving-texas-guide-driver-licenses-and-ids)

## TX-R047: Usual adult valid US transfer

Applies when: `{"age_min": 18, "valid_unexpired_us_out_of_state_license": true, "surrender_license": true}`

- Surrender the recognized license and apply with Texas documents. DPS describes knowledge/skills and adult education/ITD waivers; do not sell a first-time education or test package as mandatory.

Confidence: `official_verified`. Review required: False.

Sources: [TX-DPS-001](https://www.dps.texas.gov/section/driver-license/apply-texas-driver-license), [TX-DPS-007](https://www.dps.texas.gov/section/driver-license/moving-texas-guide-driver-licenses-and-ids)

## TX-R048: Expired out-of-state adult license

Applies when: `{"age_min": 18, "out_of_state_license_expired": true}`

- DPS moving guidance describes waivers for licenses expired not over two years, and DL-60 reserves DPS discretion to require a test. Confirm expiry dates and the actual application before recommending a waiver.

Confidence: `requires_dps_confirmation`. Review required: True.

Sources: [TX-DPS-007](https://www.dps.texas.gov/section/driver-license/moving-texas-guide-driver-licenses-and-ids), [TX-DPS-P01](https://www.dps.texas.gov/internetforms/Forms/DL-60.pdf)

## TX-R049: Minor transfer conflict

Applies when: `{"age_max": 17, "out_of_state_license": true}`

- Moving guidance says valid surrendered licenses/permits receive the equivalent Texas version; GDL guidance says all transfers obtain a Texas learner and hold six months. All minors need skills testing, but the exact transfer stage/holding requirement requires DPS confirmation.

Confidence: `conflicting_official_sources`. Review required: True.

Sources: [TX-DPS-007](https://www.dps.texas.gov/section/driver-license/moving-texas-guide-driver-licenses-and-ids), [TX-DPS-004](https://www.dps.texas.gov/section/driver-license/graduated-driver-license-gdl-and-hardship-license)

