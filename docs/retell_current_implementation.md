# Current manual Retell implementation

Updated September 14, 2026 from the user's project update. This is **user-reported progress**, not a remotely inspected configuration or executed QA. Codex has not modified Retell. This document supersedes conflicting build instructions in the historical Phase D/E packet. Existing prompts, registries and validation manifests are preserved as historical artifacts; do not regenerate them to synchronize this status.

One inbound agent, six specialist responsibilities, nine core nodes. Conversation Flow uses Rigid Mode, global GPT-4.1 mini, English US and consistent voice. Node-specific LLM and speech overrides are OFF. The global prompt is configured; internal persona changes are never announced.

| Current node | Type | Reported status |
|---|---|---|
| Main Router | Conversation, Prompt | Start node, seven semantic outgoing transitions |
| Texas License Guide | Conversation | Prompt and cross-transitions configured |
| Adult Sales Specialist | Conversation | Prompt and cross-transitions configured |
| Teen Sales Specialist | Conversation | Prompt and cross-transitions configured |
| Road Test Sales Specialist | Conversation | Prompt and cross-transitions configured |
| Booking & Scheduling | Subagent | Flow-level prompt/transitions ready; no tools attached |
| Existing Student Support | Conversation | Prompt and cross-transitions configured |
| Human Escalation | Conversation, Global ON | Global triggers and finetune examples configured |
| End Call | Ending | Talk While Waiting OFF; Global and LLM override OFF |

Main Router routes to each of the six specialists or End Call. Each specialist routes to the other five specialists or End Call. Human Escalation is globally reachable and routes to End Call. These supplied lists describe 44 local transitions plus global escalation, not an inspected canvas count. Preserve their semantic conditions.

Human Escalation has Go Back to Previous Node OFF and Prevent Immediate Re-Trigger OFF. Positive triggers include explicit staff requests, unsupported private/payment cases, unresolved high-risk policy/regulatory issues and operations that cannot safely complete. Routine confusion, sales/licensing questions and availability intent alone must not trigger it. Test repeated-entry behavior; do not silently change settings. No actual transfer is configured, so do not claim a transfer, ticket or callback.

Each conversational source says a natural goodbye before End Call. The current Ending node does not supply that goodbye. Older instructions to make every specialist a Subagent, create 21 core variables, use the older reduced edge set, or turn on ending speech **do not describe this built configuration**.

## Pending

The student_age clarification, extraction, and numeric `<18` teen / `>=18` adult Logic Split are user-reported as manually built and tested. Node-specific knowledge bases are also user-reported complete; repository source/readiness files remain the auditable reference. Functions/API/MCP tools, Cal.com/wrapper connection, production availability/writes, call transfer, private student integrations, post-call extraction, webhooks, advanced fallback/security, full simulations, voice QA and publish are pending. Configured prompts are not evidence of grounded retrieval or operational access.

The backend has five operations, persistent SQLite, mock default, gated Cal.com demo modes, America/Chicago and Dokploy backend Application artifacts. The previous suite passed 104 tests. Deployment and frontend are pending; required 120/60/30-minute Cal events are not mapped. No tools are connected in Retell, no actual Cal writes were executed by Codex, and school production writes remain blocked.

Business rules remain unchanged: adult driving plans use two-hour sessions; both known teen seven-hour plans use 2+2+2+1 driving hours without imposing that plan on observation. Road-test allocation is 30 minutes. Practice + test and PTDE allocation remain unresolved. Plano is the verified location; Allen, Frisco and McKinney remain service areas without verified operational branch/resource IDs.

The implemented age branch is specified in [minimal state and deterministic routing plan](retell_state_logic_manual_plan.md). It uses internal utilities in the same agent, not additional personas. Its remaining staged variables and tests are planning references.
