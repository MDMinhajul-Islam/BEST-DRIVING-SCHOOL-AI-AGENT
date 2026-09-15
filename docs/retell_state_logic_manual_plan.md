# Minimal state and deterministic routing — manual plan

Prepared September 14, 2026; status updated September 15. The student_age clarification, extraction and `<18`/`>=18` split are **user-reported as manually implemented and tested**. Preserve the current agent, six specialists, nine core nodes, prompts and semantic transitions. First increment: one age variable and two internal utility nodes. No tools, KB attachments, extra agents or production actions.

## A. Minimal variable registry

Create **student_age only** initially. Other fields are staged candidates, not a creation checklist. Historical `age` references must be deliberately mapped when adopted; do not maintain competing age/student_age values.

| Variable | Type / values | Writer and authority | Creation stage |
|---|---|---|---|
| student_age | Number, integer completed years; unset if unknown | Explicit caller-reported student age; Extract Student Age | First increment |
| student_or_parent | Enum: student, parent, other, unknown | Explicit relationship; targeted extraction | When persistent relationship resolves ambiguity |
| primary_intent | Enum: licensing, adult_sales, teen_sales, road_test, booking, support, other, unknown | Current expressed intent; targeted extraction | After age regression passes |
| license_status | Enum: none, learner, licensed, out_of_state, international, unknown | Caller report in License Guide; not eligibility proof | Licensing continuity |
| driver_education_status | Enum: not_started, in_progress, completed, unknown | Caller report; not verified completion | When prerequisites need persistence |
| selected_package_id | Text, canonical catalog ID | Validated catalog selection in Sales | Package handoff increment |
| selected_package_name | Text | Catalog for selected ID | Optional display convenience |
| selected_package_price | Number | Catalog base price; never caller extraction | Optional; not payment total |
| preferred_date | Text, normalized YYYY-MM-DD | Explicit clarified preference in Booking | Booking wiring increment |
| preferred_time | Text, clarified preference | Caller preference; not available slot | Booking wiring increment |
| booking_status | Enum: not_started, pending, confirmed, partial, outcome_unknown, cancelled, failed | Approved normalized backend response only | After tools and response bindings are tested |
| support_issue | Text, short non-sensitive summary | Caller report in Support | Support continuity increment |

## B. Extract Variable plan

Proposed utility: **Extract Student Age**. Ask in Main Router: **“How old is the student who will be taking the lessons?”** Wait for an answer, then extract. Skip the question if exact student age was already provided. Retell's [Extract Dynamic Variable node](https://docs.retellai.com/build/conversation-flow/extract-dv-node) supports Number fields and stores conversational values; it is not the node for conducting the age conversation.

Suggested extraction description for manual review:

> Extract completed whole years of the student taking lessons, only when explicitly stated. For a parent caller use the child's age, not the parent's. Prefer a clear latest correction for the same student. Do not infer age from permit possession, voice, grade, date of birth, relationship or teen/adult labels. Do not convert a range, fractional number, refusal or conflicting answer into an exact integer. Leave unknown age unassigned. Never default to zero or eighteen.

Keep overrides/global settings OFF and utility speech silent. Completion targets **Route Practice by Age**. Verify failed extraction and clearing behavior in simulation: do not assume an earlier student's value is automatically cleared. If stale state cannot safely be invalidated in the current UI, require a fresh explicit age for the current student before entering the split and block multi-student rollout until tested.

## C–D. Logic Split and exact targets

First case: “I already have my permit. I just need driving practice.” Preserve permit/practice context. Age unknown means ask; it does not mean guess teen/adult.

Use a narrow **Prompt transition** from Main Router to extraction when the caller wants practice/behind-the-wheel lessons and an age answer for the current student is available. The router asks first when necessary. Existing licensing, support, road-test and human intents keep their semantic paths. Do not intercept all permit mentions.

Proposed silent utility: **Route Practice by Age**, Global OFF. Retell [Logic Split](https://docs.retellai.com/build/conversation-flow/logic-split-node) evaluates on entry and requires an else destination. Configure numeric equation conditions, not a semantic Prompt decision for numeric age.

| Branch | Exact logical condition | Target |
|---|---|---|
| Teen | student_age assigned, numeric integer, 0 < student_age < 18 | Teen Sales Specialist |
| Adult | student_age assigned, numeric integer, student_age >= 18 | Adult Sales Specialist |
| Else | Unset, nonnumeric, noninteger, zero/negative, conflicting or unusable value | Main Router |

These are logical requirements, not invented Retell expression syntax. Translate them using supported current UI controls and verify numeric comparison at 17/18. Number extraction alone does not guarantee integers. If validity checks cannot be expressed, keep invalid answers in conversational clarification; do not weaken to lexical text comparisons or claim deterministic validation has been implemented. Clarify implausible values before splitting. Sales classification does not establish legal eligibility or guarantee service to a very young student.

Else resumes Main Router without a new greeting. Ask one useful clarification, then re-enter extraction only after a new useful answer. Refusal or repeated unresolved answers lead to general guidance or an offer of staff assistance, not an endless extraction loop. Human requests and goodbye retain their existing paths.

## E. Do not create yet

Do not recreate the 69-variable registry or automatically create the older 21 core definitions. Defer all staged fields above until useful. Never create LLM-owned provider keys, authentication tokens, server scopes, idempotency keys, raw Cal UIDs, refund/payment outcomes, private student records or invented branch/resource IDs. Keep slot arrays and per-session accounting server-owned until reviewed tool bindings exist. Appointment references later come only from backend results, never caller extraction.

## F. Persistence expectations

Retell [dynamic variables](https://docs.retellai.com/build/dynamic-variables) provide call context; unset placeholders are not actual ages. Verify extracted values remain readable after utility and specialist transitions. Do not assume cross-call persistence or customer verification.

Keep age across nodes for the same student. Update explicit corrections before routing. Switching caller from parent to child does not necessarily change the student; introducing a sibling/different student invalidates the old age and dependent package choices. Establish safe reset behavior manually before supporting that case. A new call starts unset unless trusted scoped setup deliberately supplies an appropriate value. Caller age remains a claim, separate from regulatory verification.

Changing intent preserves still-valid age and avoids repeated qualification. Changing package invalidates dependent display/price/session selections. Future booking state is set only by approved tool results; caller claims cannot confirm appointments. Multi-session outcomes must preserve every required session's state.

## G. Planned branch tests

These are **unexecuted manual simulations**. Record transcript, extracted value, actual route and pass/fail.

| Input / situation | Expected result |
|---|---|
| Permit + practice, unknown age | Ask student's age once and wait |
| Answer 17 | Number 17 → Teen Sales Specialist |
| Answer 18 | Number 18 → Adult Sales Specialist |
| Answer 25 | Adult; do not assume six-hour education required |
| Parent 42, child 16 | Extract 16 → Teen |
| Initial request states student is 20 | Extract 20; no repeated age question → Adult |
| “Seventeen, sorry, eighteen” | Clear correction 18 → Adult |
| “Seventeen or eighteen” / “almost eighteen” | Clarify completed exact age; no guessed value |
| Refusal, silence or “I'm an adult” | Unset/else; no invented 18 or endless loop |
| 0, -1, 17.5, unknown text or raw placeholder | Invalid/else; no accidental adult/teen routing |
| Same student Sales → Booking → Sales | Retain age and avoid repeated qualification |
| Parent introduces second child | Invalidate prior child's state; obtain new age |
| Failed extraction after earlier value | Stale value must not route; block rollout if it does |
| Licensing question replaces practice request | Existing Texas License Guide semantic path |
| Existing-student account help | Existing Student Support; age split not forced |
| Road-test availability intent | Existing Road Test/Booking path; no false escalation |
| Explicit human request during age clarification | Global Human Escalation; no false transfer |
| Goodbye during clarification | Source goodbye → End Call |

## H. Manual build order

1. Snapshot current canvas, settings, prompts and transition conditions; do not publish.
2. Create student_age as Number, verify unset handling and reference name; add no staged fields.
3. Add the two internal utilities in the same agent, overrides/global OFF. Confirm validity-condition support.
4. Wire the narrow semantic entry and numeric/else exits. Review the small age-question addition manually; do not overwrite Main Router's prompt.
5. Test 17/18, parent/child, corrections, missing/invalid/stale ages, silent utilities and loop prevention.
6. Run regression below and record actual results. Only then consider another useful variable increment.
7. Attach reviewed KB in a separate phase, connect approved tools later, and publish only after manual review/QA.

## I. Regression checklist

- Preserve one employee voice, six specialist responsibilities and nine core nodes.
- All seven original router destinations and existing specialist cross-transitions remain usable.
- Narrow age logic does not intercept unrelated intents; numeric 17/18 boundaries are correct.
- Unknown/stale values cannot route silently; no repeated greeting, question or extraction loop.
- Global escalation accepts explicit staff/private/high-risk cases and rejects routine confusion/sales/licensing/availability intent.
- Current escalation settings cannot cause repeated entry; no fake transfer, ticket or callback.
- Source goodbye is heard once; existing Ending node settings remain unchanged.
- Adult/teen driving rules and road-test 30-minute allocation remain unchanged; no observation/PTDE/practice duration inferred.
- No unattached KB/tool is treated as connected; no fabricated legal rules, prices, availability, private access or booking success.

## Later KB mapping — preparation only

| Node | Grounding scope |
|---|---|
| Main Router | Minimal intent/context guidance; no heavy indiscriminate KB |
| Texas License Guide | Reviewed DPS/TDLR regulatory content |
| Adult Sales Specialist | Verified adult catalog/business content |
| Teen Sales Specialist | Verified teen/PTDE content with unresolved allocation caveats |
| Road Test Sales Specialist | Verified services and applicable reviewed prerequisites |
| Booking & Scheduling | Internal scheduling rules; operational state only from approved tools |
| Existing Student Support | Public FAQs/policies; no private records |
| Human Escalation | Verified contact/escalation information only |
| End Call | None required |

Existing Phase F tool contracts remain the later wiring reference. Preparing this plan does not attach KB or execute the next phase.
