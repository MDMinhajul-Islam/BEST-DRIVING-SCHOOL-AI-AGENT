# Architecture

This project prepares static public business knowledge for a manually built
Retell Conversation Flow. It does not create agents, prompts, nodes, transitions
or tool connections.

1. `collector` fetches robots, then dynamically traverses sitemap XML. `robots`
   combines current crawler rules with explicit project private-route exclusions.
2. `scraper` validates each redirect before following it, spaces requests, applies
   timeouts/retries and writes a request audit. Only sitemap page URLs are fetched.
3. Original successful HTML bytes and source metadata are saved. A previous raw
   hash is compared with each new hash; failed pages are not extracted from stale
   files left on disk.
4. `cleaner` selects the public main body and emits ordered blocks with heading
   paths, lists and tables. Attribute-based package options are rendered before
   form controls are removed. Hidden public package descriptions are labeled.
5. `extractor` reads explicit page selectors, package attributes, FAQ containers,
   descriptions and public contact links. It does not fill values from model
   memory. School licensing statements are flagged for official verification.
6. `deduplicator` retains all package observations, merges exact repetitions and
   records differing known fields. Conflicting scalar package fields become null.
   Differing answers to the same FAQ are possible conflicts, not automatically
   declared contradictions. Similar topic content is never deleted through fuzzy
   matching.
7. `pipeline` creates the master JSON and category files. `renderer` creates
   reviewable Markdown and manual Retell setup references.
8. `validator` checks source references, licensing flags, price evidence, unique
   package IDs and request scope. It writes quality and coverage reports.

The master JSON is a review snapshot. `sources` includes page category, title,
URL, publisher-provided sitemap lastmod, collection timestamp, raw hash, section
and evidence. Package `observations` preserve each page-specific original record.
The `source_url` convenience field is not the complete provenance; use `sources`.

The offline command rebuilds from the last collected snapshot without network
traffic. The live command rechecks robots/sitemap and replaces structured outputs
from the current successful page set. Generated category outputs do not append.
Old raw files may remain for audit, but only the current metadata manifest is
processed. Logs append and raw originals use stable URL-derived filenames.

Dynamic schedules, student records and operational actions belong to a separate
approved backend. Regulatory verification belongs to a separate official-source
research phase.
