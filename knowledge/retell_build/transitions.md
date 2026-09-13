# Exact transitions — manual conditions

20 rule groups: 17 local edges and three shared global conditions, reduced from Phase D’s 40 explicit edges. A UI without usable global-node behavior needs 39 expanded physical edges; this is consolidation, not a claim that 20 physical edges replace all routes. Global Human, End and reroute Router reuse existing nodes, no new utility node.

| Rule | From | To | Copy condition |
| --- | --- | --- | --- |
| L01 | 01 | 02 | The caller seeks Texas licensing guidance or cannot identify the licensing pathway before a service recommendation. |
| L02 | 01 | 03 | The caller clearly wants adult education or adult driving lessons; student is 18 or older when age determines the service. |
| L03 | 01 | 04 | The caller seeks teen education, teen behind-the-wheel or parent-taught support; student is under 18 when age determines service. |
| L04 | 01 | 05 | The caller is considering the road test itself or a preparation-plus-test option. |
| L05 | 01 | 06 | The caller explicitly asks about availability, booking, an existing appointment, rescheduling or cancellation. |
| L06 | 01 | 07 | The caller has a course, payment, access, certificate or other existing-student issue rather than an appointment operation. |
| L07 | 02 | 03 | The relevant adult pathway question is resolved and the caller wants an applicable adult school service. |
| L08 | 02 | 04 | The relevant teen pathway question is resolved and the caller wants applicable teen or parent-taught services. |
| L09 | 02 | 05 | Test prerequisite understanding is resolved and the caller wants to choose a road-test package. |
| L10 | 02 | 06 | A specific licensing detour from Booking is resolved, the chosen timed package is still valid and the caller still wants to continue that appointment task. |
| L11 | 03 | 06 | The caller has selected or accepted a valid timed adult package and explicitly wants to check availability or schedule. |
| L12 | 04 | 06 | The caller has selected or accepted a valid timed teen package and explicitly wants to check availability or schedule. |
| L13 | 05 | 06 | The caller has selected or accepted a valid timed road-test package and explicitly wants to check availability or schedule. |
| L14 | 05 | 02 | The caller asks licensing requirements or reveals prerequisite uncertainty that blocks road-test recommendation. |
| L15 | 06 | 02 | A newly unanswered licensing question or prerequisite uncertainty blocks the selected appointment task; the same unresolved question has not already been referred back. |
| L16 | 06 | 07 | The issue is course/account access, payment, certificate or instruction rather than an appointment operation. |
| L17 | 07 | 06 | The caller explicitly wants an appointment lookup/change/cancel or availability operation; a private non-booking support issue has not been misclassified as booking. |
| G1 | 01, 02, 03, 04, 05, 06, 07 | 08 | The caller requests a human, a required action is unavailable, policy/eligibility/private access is unverified or a useful tool retry has failed. Do not trigger from Human or End. |
| G2 | 01, 02, 03, 04, 05, 06, 07, 08 | 09 | The caller explicitly wants to finish or confirms no further help is needed after the confirmed outcome or unresolved staff next step is explained. Do not end merely because a tool failed; do not override an unaddressed human request. |
| G3 | 02, 03, 04, 05, 06, 07, 08 | 01 | The caller explicitly changes to a different goal that this node does not own and no more specific direct edge fits. No pending action is abandoned; do not retrigger at Router or for the same unresolved detour. |

Priority by mutually excluding conditions: human request/unavailable capability → G1; explicit finish after next step → G2; direct resolved task condition → local edge; unrelated new goal → G3. Disable automatic skip/always-forward behavior for dialogue. Stay when a useful question remains; unresolved guidance goes to Human, never a default sales/booking edge.

## Loop protection

06→02 occurs only for a newly unanswered question. 02→06 requires that exact question resolved, valid package and renewed desire to continue. Otherwise staff, not repeat detour. 06→07 is non-booking support; 07→06 is an explicit appointment operation; an account/access problem does not bounce. Router global excludes Router itself; do not treat the same unhandled request as a fresh goal. Human global excludes Human/End. End is terminal. Configure supported Prevent Immediate Re-Trigger for global reroute as a backstop (three node steps is the documented default), while conditions remain the main protection. Do not delay a fresh explicit human request through a cooldown.
