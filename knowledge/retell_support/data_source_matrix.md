# Data source matrix

| Field | Source | Rule |
| --- | --- | --- |
| Program/course/package name, description, base/original price, discounts, marketing labels, included features, stated school prerequisites | STATIC WEBSITE | Use canonical sourced records; caller price challenges do not overwrite price |
| Licensing eligibility, education/test/ITD requirements and exemptions | OFFICIAL REGULATORY SOURCE | Use separate Phase B rules and review gates |
| Slot IDs, dated available times, capacity, booking status and appointment ID | LIVE OPERATIONAL API | Require live confirmed backend result; contract unknown |
| Student/caller name, contact, needs, preferred location/date/time and package preference | CALLER INPUT | Preferences and self-reported status, not verified system facts |
| Fee applicability, cancellation exceptions, refund/reschedule authority, manual enrollment exceptions | INTERNAL BUSINESS RULE | Obtain owner-approved policy; preserve public fee evidence separately |

`package_price` comes from `package_catalog.current_price` and currency/snapshot status; no caller amount becomes authoritative. Office hours, duration and generic weekend scheduling are static; actual slots are live. A license-guide answer does not establish school authorization or book a package.

## Phase C.1 / D authority matrix

| Information | Authority | Treatment |
| --- | --- | --- |
| Package price/contents | Best Driving School catalog website snapshot | Reviewed business facts, not caller-editable |
| Texas eligibility | Reviewed DPS/TDLR records | Regulatory; suppress disputed rules |
| Driving duration/remainder | CTO / INTERNAL BUSINESS RULE | BUSINESS VERIFIED, enforcement unverified |
| Road 20+5+5 / 30 allocation | CTO / INTERNAL BUSINESS RULE | BUSINESS VERIFIED; frontend conflict preserved |
| Available time | Approved live read endpoint | Ephemeral observation, not reservation |
| Selected preference | Caller input | Tentative |
| Confirmed booking | Authorized explicit backend success + appointment ID | Environment-aware guard |
| Student account | Scoped authenticated system | Unavailable today; staff |
| Mock result | Synthetic adapter | Demo only |
