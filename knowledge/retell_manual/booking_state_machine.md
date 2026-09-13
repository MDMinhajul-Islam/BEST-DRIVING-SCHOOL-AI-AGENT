# Booking state machine

Manual design documentation only. No Retell agent, workflow, state or tools have been created or modified.

State is guarded, not free-text model confidence.

| From | To | Guard |
| --- | --- | --- |
| NO_PACKAGE | PACKAGE_SELECTED | Valid catalog selection |
| PACKAGE_SELECTED | AVAILABILITY_NEEDED | Known requirement and fresh slots needed |
| AVAILABILITY_NEEDED | AVAILABILITY_CHECKED | Successful correct-mode read; no confirmation |
| AVAILABILITY_CHECKED | SLOT_OPTIONS_PRESENTED | Describe returned observations and limitations |
| SLOT_OPTIONS_PRESENTED | SLOT_SELECTED | Caller selects returned authoritative compatible slot; current live labels cannot satisfy this gate |
| SLOT_SELECTED | SESSIONS_PARTIALLY_SELECTED | Fewer than required multi-session choices |
| SESSIONS_PARTIALLY_SELECTED | ALL_SESSIONS_SELECTED | All compatible tentative choices; not booked |
| SLOT_SELECTED | BOOKING_PENDING | Single session approval + verified customer + ready backend contract + authorized environment |
| ALL_SESSIONS_SELECTED | BOOKING_PENDING | Approval and verified transaction semantics; no assumed atomicity |
| BOOKING_PENDING | BOOKING_CONFIRMED | EXPLICIT_BACKEND_SUCCESS: correct-mode success AND returned appointment ID(s) AND booking_confirmed=true. Real confirmation additionally production_write_enabled=true AND backend_success_verified=true; mock always demo. |
| BOOKING_PENDING | BOOKING_FAILED | Explicit negative backend result; timeout remains pending reconciliation |
| BOOKING_FAILED | AVAILABILITY_NEEDED | Race: clear stale slot, refresh and obtain new choice |
| NO_PACKAGE | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| PACKAGE_SELECTED | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| AVAILABILITY_NEEDED | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| AVAILABILITY_CHECKED | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| SLOT_OPTIONS_PRESENTED | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| SLOT_SELECTED | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| SESSIONS_PARTIALLY_SELECTED | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| ALL_SESSIONS_SELECTED | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| BOOKING_PENDING | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| BOOKING_CONFIRMED | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |
| BOOKING_FAILED | HUMAN_ESCALATION | Capability unavailable, private access, alignment/policy gap or repeated failure |

Only BOOKING_PENDING → BOOKING_CONFIRMED can confirm, with EXPLICIT_BACKEND_SUCCESS. Availability, selection, native form submission, caller payment claim or timeout cannot satisfy it. Current production_write_enabled=false prevents all real confirmation. Mock requires mode=mock, synthetic=true, production=false and MOCK appointment identity; spoken confirmation always demo reservation. Cancelled result has booking_confirmed=false, not an active reservation.

Write timeout stays pending/outcome unknown; preserve same action key and reconcile before retry. Explicit failure becomes BOOKING_FAILED; race refreshes availability and gets a new selection. Date/location/package changes return to AVAILABILITY_NEEDED. Multi-session partial successes record only confirmed appointment IDs and escalate remaining work; never silently cancel already-confirmed sessions or claim all confirmed.

Lookup: known reference → secure scoped verification → backend find → verified identity. Reschedule: lookup/version → fresh compatible slots → caller approval → atomic replacement → explicit result; old reservation stays until success. Cancel: scoped verification + approved policy + caller confirmation → backend cancel → explicit cancelled status. Refund is distinct and unimplemented. All production lookup/change/cancel currently escalate.
