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
is pending. Future tools are specified only in
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
