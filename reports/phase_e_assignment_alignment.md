# Phase E assignment alignment

The manual packet retains Phase D business logic while reducing conversational state and grouping transitions. All original Phase D sources remain unchanged. One intended agent, six specialist responsibilities, nine flow nodes; no Retell configuration modified or import JSON created.

| Requirement | Packet coverage |
| --- | --- |
| One inbound agent / six specialist behaviors | One agent, nodes 02–07; global rules plus Router/Human/End |
| Semantic routing | Meaning-based router and exact guarded conditions |
| Shared context | 21 core definitions, built-in extraction, conditional transcript facts, no repeated greeting |
| Business accuracy | Canonical catalog owns package/price; caller cannot overwrite |
| Regulatory accuracy | Generated safe-only DPS/TDLR view; disputed rules excluded, CTO separate |
| Recommendation | Relevant education/lesson/test comparison; no pressure or readiness guarantee |
| Live availability boundary | Approved reads only, no static time grid; unknown IDs/timezone/resources acknowledged |
| Booking boundary | Demo records explicitly synthetic; production writes/lookup unavailable |
| Support / staff | Public FAQ versus private records; no invented ticket/transfer/refund |
| Intent switch / loop protection | Global reroute exclusions, resolved detour requirement, no account-booking bounce |
| Voice naturalness | 1–3 sentences, one question, interrupt-friendly, no persona introductions |
| Assignment QA/demo evidence | Six smoke tests + existing 21 scenarios planned; actual calls/three recordings pending humans |

## Counts and honest readiness

- phase d variables: 69
- core variables: 21
- conditional variables: 20
- backend only variables: 16
- deferred variables: 4
- redundant removed: 8
- flow nodes: 9
- specialists: 6
- local edges: 17
- global rules: 3
- transition rules: 20
- expanded edges: 39

Twenty rule groups versus 40 Phase D explicit transitions: 17 local + three global conditions. Expanded fallback has 39 actual node-pair edges, so the physical graph reduction is modest; the main gain is configuring shared global behavior once. No useful source concepts deleted.

All copy-paste prompts and manual sheets are ready. Existing local mock demonstrates five operation mechanics and default-disabled live read adapter exists. Hosted authenticated tool wrapper is not deployed, so actual Retell demo/read wiring remains pending approved integration. Faithful multi-session duration fixtures remain required. Production lookup/writes remain blocked. Human manual build can begin with knowledge/routing/extraction/fallback; no successful tool call or voice recording is claimed.

## Validation

72/72 automated tests pass (62 preserved, 10 new Phase E checks), using `.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests`. Checks cover source hashes, all 69 variable decisions, unique valid nodes/destinations, prompt presence, server-state isolation, unsupported-write rejection, honest grouped/expanded edge counts, catalog-price authority, explicit environment-aware tool confirmation, unchanged teen/road arithmetic and safe-only regulatory export. No Retell call or actual voice test was executed. `git diff --check` passes.
