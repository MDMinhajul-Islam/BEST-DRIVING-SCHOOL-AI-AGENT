# Manual build order

Human actions only; no remote Retell changes were made. Logical steps avoid unverified button labels. Platform references checked 2026-09-13: [Subagent tool/state support](https://docs.retellai.com/build/conversation-flow/subagent-node), [dynamic-variable extraction](https://docs.retellai.com/build/single-multi-prompt/extract-dv), [prompt versus equation conditions](https://docs.retellai.com/build/conversation-flow/transition-condition), [global transitions](https://docs.retellai.com/build/conversation-flow/global-node), [End closing prompt/global setting](https://docs.retellai.com/build/conversation-flow/end-node). These support nine nodes without additional extraction utility nodes.

1. Open or manually create ONE non-production agent for this build; no separate agents for personas.

2. Choose Conversation Flow and keep all nine nodes in the same flow.

3. Copy knowledge/retell_build/global_prompt.md into agent global behavior; choose one fixed mode using tool_mapping.md.

4. Configure the 21 CORE state definitions/types/defaults from variable_registry.md; do not add server controls or all 69 variables.

5. Create 01 Greeting / Router as start Subagent; paste 01_router_prompt.md.

6. Create 02 Texas License Guide as Subagent; paste its prompt.

7. Create 03 Adult Sales as Subagent; paste its prompt.

8. Create 04 Teen Sales as Subagent; paste its prompt.

9. Create 05 Road Test Sales as Subagent; paste its prompt.

10. Create 06 Booking & Scheduling as Subagent; paste its prompt, leave unready booking tools unattached.

11. Create 07 Existing Student Support as Subagent; paste its prompt.

12. Create 08 Human Escalation as Subagent; paste its prompt. No transfer/intake tool without reviewed configuration.

13. Create 09 End Call as End node; enable Speak During Execution with Prompt and paste its closing prompt.

14. Add 17 local conditions and global conditions for existing nodes 01/08/09 from transitions.md; exclude self/repeat triggers. Do not enable automatic skip-forward on dialogue.

15. Attach only mapped reviewed knowledge from knowledge_mapping.md, minimal global knowledge. Verify school contacts and snapshot freshness.

16. Add built-in Extract Dynamic Variable to 01–08 for allowed caller fields, not security/confirmation fields. Configure approved response bindings for tool-backed state only after tested wrapper exists. Isolated demo tools or approved read-only adapter require a real approved authenticated URL/schema; none is deployed in this repository. Otherwise retain safe staff fallback.

17. Run the six smoke tests below in the selected mode; record actual outcomes.

18. Fix incorrect routing, repeated questions, source retrieval, mode labeling, missing extraction or loops; rerun affected smoke cases.

19. Run all 21 Phase D scenarios from knowledge/retell_manual/test_matrix.md with the lean state mapping; keep transaction keys/versions server-side. Record at least 14 actual calls and three demo recordings per assignment; plans are not execution results.

## Mandatory smoke tests

| Test | Expected path | Expected variables | Response behavior |
| --- | --- | --- | --- |
| Adult first-time license | 01 → 02 → 03 only for applicable service | age, license_status, driver_education_status | Usual reviewed pathway; no automatic purchase or guarantee |
| Teen package inquiry | 01 → 04; 02 if eligibility uncertain | age, student_or_parent, package_id, package_price | Catalog contents/base price; no classroom-law conflation |
| Adult lesson to Booking | 01 → 03 → 06 → 08 production | package_id, session_count_required, session_plan, preferred_date | Six hours means three two-hour sessions; demo only after tool success |
| Road Test to Booking | 01 → 05 → 06 → 08 production | road_test_eligibility, package_id, preferred_date | No pressured practice, no fabricated aligned time |
| Existing student support | 01 → 07 → 08 private issue | support_issue, support_category, escalation_reason | Public help or staff; no invented account/payment action |
| Mid-call intent switch | 03 → global 01 → 06 → 08 production | primary_intent, known age/package, escalation_reason | No repeated greeting/qualification; no unrelated sales package used to identify old booking |

Actual results/recordings: pending human manual build. A smoke test cannot pass a booking success branch with an unattached tool. First build can test routing/knowledge/fallback now; successful demo booking branches require the documented approved wrapper/fixtures. No production payment or booking modifications are part of acceptance.

## MVP versus Production Extension

MVP: nine nodes, 21 core definitions, optional relevant conditional fields, source-limited retrieval, semantic conditions, natural one-employee voice and explicit safe fallback. Built-in extraction persists reported facts; tool results persist action display fields only after approved wiring.

Production Extension: authoritative mappings/timezone/resources; authenticated scoped verification; atomic or explicit per-session accounting; durable idempotency/versions; unknown-outcome reconciliation; cancellation/refund/payment/pickup policies; actual intake/transfer; privacy/retention. These are server/business requirements, not extra MVP LLM variables. Rare credential/certificate detail variables are conditional, CRM/parallel goals deferred. No additional planning phase is required to start manual knowledge/routing build; missing integration cannot be hidden or invented.
