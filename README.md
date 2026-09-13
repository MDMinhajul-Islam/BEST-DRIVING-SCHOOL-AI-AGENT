# Best Driving School knowledge pipeline

A Python pipeline that collects public business knowledge for Best Driving
School, Texas, and prepares sourced JSON, Markdown and manual Retell setup
references.

**The scraper does NOT build or modify the Retell Conversation Flow.** It
prepares business knowledge and supporting artifacts for a manually configured
Retell AI agent. It does not create bookings, enroll students, take payments or
access private accounts. Review the generated data before use in a voice agent.

## Install and run

Python 3.10+ is supported; this snapshot was exercised on Python 3.14.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.main
```

Or activate a Python environment, install requirements and run `python -m src.main`.
Run from this repository root. Paths resolve from the repository rather than the
current output directory.

Rebuild extraction from the previously saved snapshot without network requests:

```powershell
.\.venv\Scripts\python.exe -m src.main --offline
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The live command reads robots, discovers sitemap URLs dynamically, checks scope,
scrapes allowed pages, saves raw bytes, cleans/extracts, writes knowledge and
validates. It prints coverage counts. Exit 0 means structural/source checks passed;
it does not mean semantic approval. Exit 1 indicates failed/empty public pages;
exit 2 indicates validation errors. Bootstrap/sitemap errors stop the run.
Offline mode requires the previous discovery, raw HTML and metadata files.

## Architecture and scraping

Sitemap → robots/scope checks → polite requests → raw HTML + metadata → ordered
content blocks → deterministic extraction → exact deduplication + conflict
tracking → JSON + Markdown → validation and coverage reports.

The sitemap is the live public page inventory; no fixed list of 18 pages is used.
Current robots restrictions and project private-route exclusions are enforced
before every page request and redirect. Requests use a clear user agent, spacing,
timeouts, limited retries and logging. Links are recorded for reference but are
never traversed as a crawler frontier. No browser automation is used because the
relevant content is server-rendered.

See [initial assessment](docs/site_assessment.md), [architecture](docs/architecture.md)
and [scraping strategy](docs/scraping_strategy.md).

## Files

```text
src/                 discovery, fetching, cleaning, extraction, reporting
config/settings.py   site, user agent, timeout, delay and exclusions
tests/               offline safety and extraction regressions
data/discovery/      robots, sitemap originals, manifest and request audit
data/raw_html/       original successful HTML bytes; stable URL-derived filenames
data/cleaned/        ordered blocks as JSON and Markdown
data/structured/     business, services, courses, pricing, FAQ, policies,
                     locations, links, page metadata, conflicts, master knowledge
knowledge/           human-readable category documents and source index
knowledge/regulatory/ official verification placeholder; no fabricated official facts
knowledge/retell_support/ manual intent, persona, variables, source and gap references
docs/                assessment, architecture, scraping and integration design
reports/             automated quality/coverage/validation and review evidence
logs/                append-only scraper log
```

Start review with [knowledge_base.json](data/structured/knowledge_base.json),
[courses and pricing](knowledge/courses_and_pricing.md),
[quality report](reports/data_quality_report.md) and
[coverage](reports/knowledge_coverage.md). Manual Retell setup references are in
[knowledge/retell_support](knowledge/retell_support).

## Provenance, updates and conflicts

Each significant record retains `sources`: URL, title, page type, sitemap lastmod,
scrape time, section, raw hash and evidence. Packages retain original observations
from each source page. Missing extracted fields are null. Selector prices, original
prices and narrative/per-hour price claims are kept distinct. Differing package
fields are reported and cleared rather than silently selecting a winner. Different
FAQ answers are retained as possible conflicts for review.

Exact duplicate content is consolidated with source lists retained. No fuzzy
subject-matter deletion is used. Structured outputs are rebuilt on every run and
do not append records. New raw hashes are compared to the last collection and
changed pages are reported. Offline rebuilds do not alter raw collection evidence.
Raw hashes may change because of generated form tokens. Cleaned hashes track
public-content changes separately; changes to extraction logic can also change
cleaned hashes and must be distinguished from website edits during review.
Old raw files can remain on disk, but only successful current-manifest pages are
processed. Failed retrievals are reported instead of silently using stale content.

## Static versus operational knowledge

Static: public services, packages, prices, FAQ, policies, contacts and service areas.
Live: slot availability, bookings, student accounts, enrollment and payments.
Public enrollment forms and upcoming batches are excluded from the knowledge base.
Public purchase links are references, not operations or availability evidence.

School licensing statements are flagged `requires_official_verification: true`.
They are not official legal facts. [Regulatory research](knowledge/regulatory/README.md)
now contains a separate reviewed Phase B layer with explicit uncertainty gates. Future tools are specified only in
[operational requirements](docs/operational_data_requirements.md) and
[booking integration plan](docs/booking_integration_plan.md).

## Manual Retell use and limitations

Review sources, conflicts, missing fields and freshness; resolve school policy
questions and officially verify licensing guidance. Then manually choose the
relevant records/documents for each persona using the knowledge map and proposed
shared variables. Do not upload conflicting raw statements as approved answers.

Deterministic extractors are tailored to the current school markup. Unknown page
types still receive cleaned blocks and source metadata, but new package/FAQ markup
may need selector changes. Age and hour fields are deliberately conservative;
null does not prove that no requirement exists. Service-area pages do not establish
additional offices. Automated validation checks source/schema integrity, not full
semantic truth or legal compliance. Narrative pricing binding and contradictions
across differently phrased statements still require human review. Live operational
data and actual Retell behavior are outside this phase.

## Phase B — official Texas knowledge

Regulatory research date: 2026-09-13.

Phase B adds a source registry, preserved government evidence, 56 conditional
rules, 11 applicant pathways, and 13 potential school-package relationships.
The master file keeps all Phase A keys and adds only `regulatory_reference`.
School licensing text and historical conflicts remain unchanged.

Start with [manual review](reports/phase_b_manual_review.md),
[coverage](reports/regulatory_coverage.md), and
[official-source index](knowledge/regulatory/source_index.md).
The reviewed source set contains 13 DPS pages, 10 TDLR pages and four PDFs.
Two PDFs have archived originals; two DPS PDFs have web-tool extracts because
direct downloads timed out. Unavailable sources are explicitly unreviewed.

```powershell
.venv\Scripts\python.exe -m src.regulatory
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The rebuild is offline and checks evidence anchors, hashes, schema and references.
For a public-source refresh, run `python -m src.regulatory_collect` first.
Changed or failed sources cannot silently approve dependent rules. Review changes,
update the curated rule configuration and research date, then use the explicit
curator flag `python -m src.regulatory --review-current` only after actual review.
This flag does not bypass missing evidence or failed retrieval. Recheck before
production and at least every 90 days afterward.

General adult guidance is supported. Teen classroom totals, PTDE daily limits,
adult ITD selection, minor transfers and vehicle-inspection paperwork have official
discrepancies. Adult restricted-license/TPST gates, foreign cases and exceptions
require confirmation. These details are blocked by `review_required`; tests prove
traceability and integrity, not individual licensing eligibility. Retell support
documents are references for future manual configuration. No workflow or booking
integration is implemented.

## Course / package / pricing audit

The saved public snapshot contains five purchasable program families, six course
pages and 13 unique package options. Four service-page categories are a different
count; homepage/location wording sometimes calls the five program cards “courses.”
The audit reconciles that naming explicitly. Ninety-one raw option observations
consolidate to 13 packages; no previous canonical duplicate was removed.

Review [audit findings](reports/course_package_pricing_audit.md),
[package catalog](knowledge/package_catalog.md),
[hierarchy](data/structured/course_package_booking_map.json), and
[schedule versus availability](docs/schedule_vs_availability.md).
All 13 prices match the saved evidence; this audit does not perform a live price
refresh. Marketing labels, discounts and the 3% online processing fee have separate
fields. Twelve options need live scheduling; self-paced online education uses an
access/purchase process rather than a timed appointment.

```powershell
.venv\Scripts\python.exe -m src.main --offline
.venv\Scripts\python.exe -m src.package_audit
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Run the package audit after business regeneration to refresh the separate catalog.
It does not collect restricted routes or implement booking. Readable package IDs
retain legacy IDs for migration; neither includes price. Operational field names,
slots, checkout totals and service-specific cancellation rules require later
authorized inspection. Official Phase B research remains separate and unchanged.


## Phase C booking investigation

Public frontend evidence and three date-only anonymous availability reads are documented in `reports/phase_c_booking_investigation.md`. All 13 canonical packages are preserved. Twelve form product IDs are provisional; authoritative backend identity, operational location IDs and production transaction contracts remain unverified.

Offline assembly: `.venv\Scripts\python.exe -X utf8 -m src.booking.investigate`. Synthetic five-operation demo: `.venv\Scripts\python.exe -X utf8 -m src.booking.demo`. Tests: `.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v`. The demo writes `reports/phase_c_mock_demo.json` and never contacts the school.

`BestDrivingSchoolBookingAdapter` defaults to live disabled. Explicit enablement permits only the three evidenced GET routes, with date only and no redirects. Production create/find/reschedule/cancel stay disabled. `MockBookingAdapter` is in-memory synthetic data with verification, idempotency, capacity conflict and atomic update checks. No Retell configuration or production booking was changed. See `docs/retell_booking_tool_contracts.md` for proposed manual integration contracts.


## Phase C.1 and D manual blueprint

CTO-confirmed scheduling rules are internal business facts, distinct from website observations and Texas regulations. Seven known driving package plans and two road-test models are reconciled without claiming backend enforcement. PTDE/observation behavior remains unresolved.

Rebuild in order: `.venv\Scripts\python.exe -X utf8 -m src.manual_retell.business_rules`, then `.venv\Scripts\python.exe -X utf8 -m src.manual_retell.blueprint`. If regenerating Phase C, always run both afterward. Master document: `docs/retell_manual_build_spec.md`; diagram: `docs/manual_retell_flow.md`. Offline validation schema under `data/design` is for tests only and is not a Retell workflow import.

Ten conceptual nodes, 69 shared variables, 40 handoffs, nine persona prompts and 21 expected-call scenarios. Retell remains untouched; production writes/lookup blocked. Local mock validates mechanics, with duration-aware fixtures and authenticated wrapper still needed before faithful multi-session demos. No actual voice calls or recordings claimed. Run the full unittest suite before manual build.


## Phase E lean manual packet

Use `docs/retell_manual_implementation_sheet.md` beside Retell and follow `docs/retell_manual_build_order.md`. Copy-paste prompts are under `knowledge/retell_build/prompts/`; global prompt is separate. Nine flow nodes, 21 core state definitions, 20 conditional, 16 server-only, four deferred and eight redundant concepts; all Phase D sources preserved. Twenty transition rule groups mean 17 local edges plus three global conditions (39 expanded pairs if global behavior unavailable).

Regenerate offline with `.venv\Scripts\python.exe -X utf8 -m src.manual_retell.build_packet`. The new validation manifest is a static test artifact, not a Retell workflow import. Current local mock/read adapters need an approved hosted wrapper before Retell tool wiring; production lookup/writes stay blocked. Manual knowledge/routing/extraction/fallback build can start now. Smoke tests and 21-call QA are plans, not executed results.

## Phase F demo booking backend

The authenticated five-operation HTTP wrapper now supports a restart-safe, duration-aware mock and Cal.com API v2 demo adapter. Start with a private RETELL_TOOL_SECRET and BOOKING_MODE=mock; run `.venv\Scripts\python.exe -m uvicorn src.routes.booking:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log`. Environment variables are explicit; .env files are not automatically loaded. Run the full unittest command above for 104 tests (72 prior + 32 Phase F).

Read `docs/calcom_setup_guide.md`, `docs/retell_calcom_tool_wiring.md`, and `docs/dokploy_application_deployment.md`. Dokploy uses backend Application mode with the root Dockerfile and a durable `/app/runtime` volume. Frontend work is deferred. Cal event mappings remain null: the existing public 45-minute events do not match the required 120/60/30-minute events. No Cal write, deployment, or Retell change has occurred. Readiness and remaining configuration are recorded in `reports/phase_f_calcom_integration.md`.
