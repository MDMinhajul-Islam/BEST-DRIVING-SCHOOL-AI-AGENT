# Knowledge source map

| Data | Source | Readiness |
| --- | --- | --- |
| Services, packages, prices | Public school sitemap pages | Extracted; manual review required |
| FAQ and policy text | Public school pages | Preserved; review applicability and conflicts |
| Locations and contacts | Public school content | Distinguish office from service areas |
| Texas licensing requirements | DPS/TDLR official sources | Not collected; verification pending |
| Availability, bookings | Approved school scheduling backend | REQUIRES API |
| Enrollment, accounts, payments | Authenticated school system | REQUIRES AUTHENTICATED SYSTEM |

Each structured record has `sources` with URL, title, page category, sitemap lastmod, scrape time, heading/section and evidence where practical. Package `observations` preserve page-specific values. Raw HTML and request audit are under `data/`. A sitemap date is not a freshness guarantee.

See [source index](../source_index.md), [quality report](../../reports/data_quality_report.md) and [coverage](../../reports/knowledge_coverage.md).

## Phase B authority separation

| Fact/action category | Source of truth |
| --- | --- |
| BUSINESS FACT | Best Driving School public website and reviewed Phase A observations |
| REGULATORY FACT | Current reviewed Texas DPS / TDLR official records; Phase B rule IDs and evidence |
| LIVE AVAILABILITY | Approved scheduling API, later integration |
| BOOKING ACTION | Confirmed booking backend result, later integration |
| STUDENT-SPECIFIC INFORMATION | Authenticated student system, later integration |

The earlier Phase A “not collected” regulatory row is a historical baseline; this Phase B section supersedes its readiness statement. School guidance remains historical business evidence and is not elevated to law. The master `regulatory_reference` points to the separate official layer. Proposed service relationships remain conditional.
