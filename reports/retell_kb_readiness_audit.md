# Retell Knowledge Base readiness audit

Audit date: September 15, 2026. Repository state only; no Retell modification, deployment, Cal.com connection or production action was performed.

## Verdict

**READY AFTER MINOR CLEANUP.** Seven clean, node-specific upload candidates now exist. They are suitable for manual review/upload as a controlled set, but official regulatory material must be refreshed by December 12, 2026 (or sooner if a source changes), business prices must be reconfirmed before production quoting, and the conflicting public operating-hours claims need business confirmation. Retell retrieval and spoken-answer QA have not been executed.

## 1–2. Inventory and classification

The complete path-by-path inventory is [retell_kb_inventory.md](retell_kb_inventory.md). It records exact path, format, purpose, source class, canonical/intermediate class and upload suitability for **349 pre-audit files** under `data/`, `knowledge/`, `docs/` and `reports/`.

| Classification | Files | Treatment |
|---|---:|---|
| Canonical | 28 | Structured domain sources, curated regulatory topics, and two reviewed exports; source layer for clean KBs |
| Intermediate | 119 | Cleaned pages, derived maps, generated knowledge/design; do not upload directly |
| Evidence captures | 106 | Regulatory and operational captures/metadata; preserve, do not upload |
| Raw | 31 | HTML/XML or raw source; preserve, do not upload |
| Audit reports | 43 | QA evidence, not caller knowledge |
| Project documentation | 22 | Architecture/integration instructions, not caller knowledge |

The 28 canonical items comprise 11 selected structured JSON files, 15 curated `knowledge/regulatory` topic/index files, and `knowledge/retell_build/reviewed_license_knowledge.md` plus `scheduling_knowledge.md`. “Canonical” does not mean directly retrieval-ready: large nested JSON and unresolved-question/source-index documents are source layers. Seven newly created ready documents are outside the 349-file pre-audit denominator.

Raw HTML, scraped page dumps, regulatory HTML/PDF/text captures, inspection excerpts, discovery artifacts, operational evidence, and per-page cleaned JSON/Markdown remain traceability evidence. They contain navigation repetition, duplicate observations, machine fields, or volatile details and must not become Retell KBs.

## 3. Website cleanliness and conflicts

Existing pipeline reports verify 18/18 public pages processed, 5 programs, 6 courses, 13 canonical packages, 13/13 verified base prices, 102 canonical FAQ Q&As and four Best-selling labels. The two supplied teen examples agree with the canonical catalog: Classroom + Driving is $399 with 24 classroom/7 driving/7 observation and Best selling; Behind the Wheel Only is $350 with 7 driving/7 observation.

Package audit found 91 raw observations, 78 duplicate observations consolidated, zero duplicate canonical packages, and zero package-price conflicts. Exact deduplication merged 97 FAQ, 156 contact, 191 fact, 229 licensing and 1,215 link repetitions while retaining sources. There are **149 unbound narrative price claims**; they were not promoted to package prices.

Eight unresolved website conflicts remain:

1. Plano location wording.
2. Claimed TDLR licensing wording.
3. International-driver lesson wording.
4. Weekend availability wording.
5. Parent-taught professional lesson wording.
6. First-attempt pass guarantee wording.
7. Terms platform age restriction versus teen services.
8. Adult education applicability wording.

Broad `knowledge/faq.md`, `knowledge/policies.md`, `knowledge/business_overview.md`, `knowledge/locations.md`, cleaned page Markdown, and `data/structured/knowledge_base.json` are not upload-ready. They mix unresolved regulatory claims, repeated source links, navigation/marketing prose, conflicting hours or irrelevant legal text. The ready set includes only checked package facts and narrowly scoped support/contact statements.

## 4. Regulatory authority

`data/structured/texas_regulatory_knowledge.json` is the canonical rule registry. Records carry rule IDs, conditions, official source IDs/URLs, evidence paths and hashes, verification dates, confidence, review flags and safe-for-guidance flags. `knowledge/retell_build/reviewed_license_knowledge.md` exports only `official_verified`, safe-for-general-guidance, non-review-required records. DPS/TDLR authority takes precedence over school marketing for licensing rules.

The regulatory research date is September 13, 2026. The freshness report sets December 12, 2026 as the next recheck for reviewed sources. Several source publication dates are unknown; some official pages date to 2020–2024. Four DPS HTML sources and two DPS PDFs are FETCH_FAILED/not reviewed; one TDLR PDF is SOURCE_REMOVED; one DPS third-party-testing source also requires review. These unavailable sources are evidence gaps, not proof that rules changed. Records marked review-required, disputed, or date-uncertain are excluded from the ready export unless a separately corroborated rule is explicitly approved by the canonical registry.

Adult first-time, teen/learner, parent-taught, driver education, road test, new-resident and international topics exist. They support general conditional guidance, not individualized eligibility. Adult permits, provider-specific third-party-test admission, foreign-license edge cases, document variations and unresolved exceptions must follow the export's limitations or escalate. School-site licensing statements must never override official guidance.

## 5–6. Unsafe/stale and operational leakage findings

The audit counts **165 unsafe/stale review items**: 8 explicit website conflicts, 149 unbound narrative price claims, and 8 unavailable regulatory source records requiring review. These categories are kept separate and may refer to related subject matter.

Static KBs must exclude slots, provider availability, confirmations, booking/customer/account records, payment/certificate/refund states, Cal UIDs, tokens and transaction results. The ten `data/operational_evidence` files, Phase C mock output, Cal event observation/mapping, booking maps, backend maps and requirements are implementation evidence, not upload knowledge. Existing frontend/form IDs for 12 packages are provisional observations and cannot be presented as authoritative backend IDs. The generated ready documents contain no operational IDs.

Static scheduling rules are allowed and labeled **INTERNAL BUSINESS VERIFIED**: standard driving session 120 minutes, verified odd remainder as the final shorter session, adult 2/4/6/8/10-hour plans, teen 2+2+2+1 driving plan (not observation), and road-test 20+5+5 = 30-minute allocation. Unknown PTDE allocation and Practice + Road Test duration remain excluded/flagged.

Plano is the verified school/testing location. Allen, Frisco and McKinney remain advertised service areas, not independent branches. The public phone/address are included. Conflicting “9am–7pm” and “Helpline 24/7” hours are excluded pending confirmation.

## 7. Files safe to use as-is

Use the seven files under `knowledge/retell_kb_ready/` after a final human read and before their stated refresh boundary. The copied regulatory and scheduling exports retain their original source/authority headers. The five new business/contact files trace claims to canonical JSON and public URLs.

No older broad business knowledge file is recommended as-is. The canonical JSON files remain safe source data for programmatic validation, not preferred Retell uploads due to nesting and retrieval noise.

## 8. Files requiring cleanup or confirmation

- `knowledge/faq.md`, `knowledge/policies.md`, `knowledge/business_overview.md`, `knowledge/locations.md`: require claim selection, conflict resolution and source-link deduplication before any future upload.
- `data/structured/faq.json` and `policies.json`: require approval filtering; many records remain `pending_manual_review` or require official verification.
- `knowledge/regulatory/*`: individual topic files are traceable but include unresolved/edge-case context; use the reviewed export instead and refresh official sources.
- Hours require business confirmation. Prices require freshness confirmation before production quoting.
- The seven ready documents still require manual Retell upload and retrieval QA; this audit does not certify the platform behavior.

## 9. Files that must not be uploaded

Do not upload directories `data/raw_html`, `data/inspection`, `data/discovery`, `data/regulatory_sources`, `data/operational_evidence`, `data/design`, `data/cleaned`, `knowledge/retell_build/prompts`, `knowledge/retell_manual`, or `reports`. Do not upload backend/source code, raw/large `data/structured/knowledge_base.json`, maps containing provisional frontend IDs, Retell prompts as KB content, test matrices, architecture docs, booking ledgers or environment/configuration files.

## 10. Exact node-to-file mapping

| Retell node | Upload files |
|---|---|
| Main Router | None |
| Texas License Guide | `knowledge/retell_kb_ready/texas_license_guide/official_texas_guidance.md` |
| Adult Sales Specialist | `knowledge/retell_kb_ready/adult_sales/adult_services_and_prices.md` |
| Teen Sales Specialist | `knowledge/retell_kb_ready/teen_sales/teen_services_and_prices.md` |
| Road Test Sales Specialist | `knowledge/retell_kb_ready/road_test_sales/road_test_services.md`; plus the Texas official guide only if node-specific prerequisite retrieval is required and tested |
| Booking & Scheduling | `knowledge/retell_kb_ready/booking_rules/internal_scheduling_rules.md` |
| Existing Student Support | `knowledge/retell_kb_ready/existing_student_support/public_support_boundaries.md` plus Adult/Teen/Road Test file only when public package questions need them; avoid duplicating all files initially |
| Human Escalation | `knowledge/retell_kb_ready/human_escalation/verified_contact.md` |
| End Call | None |

Avoid uploading the regulatory guide twice until cross-KB retrieval behavior is tested. If Retell cannot share KBs selectively, create a small road-test prerequisite excerpt from the same approved rule IDs rather than attaching every regulatory topic.

## 11. Missing knowledge

- Business-confirmed public/phone operating hours and actual escalation/transfer process.
- Refreshed resolution for eight website conflicts and approval of relevant FAQ/policy subsets.
- Current authoritative verification of school/provider licensing claims if they will be spoken as current status.
- Confirmed Practice + Road Test duration and PTDE instructor/booking allocation.
- Verified pickup/drop-off policy and operational service-location/resource mapping.
- Production booking identifiers and current operational state belong to tools, not KB.
- Private support, payment, refund, certificate and student-record behavior requires approved systems/tools.
- Recorded Retell retrieval tests for correct sources, refusal/escalation behavior, cross-node leakage and price freshness.

## Audit totals

- Files inspected: **349**
- Canonical knowledge files: **28**
- Raw/intermediate/evidence/audit/documentation files: **321**
- Explicit content conflicts: **8**
- Unsafe/stale review items: **165**
- Retell-ready files created: **7**

The repository is ready for a controlled manual KB attachment after the minor confirmations above. It is not evidence that the KBs are already attached, that Retell retrieval works, or that operational tools are available.
