# Public scraping strategy

The collector uses a declared user agent, at least 0.5 seconds between request
starts, a 30-second timeout and up to three attempts for transport failures and
429/500/502/503/504 responses. Retry-After numeric values are respected up to a
30-second wait; other cases use backoff. Non-retriable status errors are recorded.
Public access does not permit private operational discovery in this project.

Robots is fetched first and failure/invalid HTML stops collection. Sitemap indexes
are supported with cycle detection and a 30-document safety limit. Sitemap dates
are retained as published, not interpreted as verification. URL normalization
limits requests to this school domain, collapses dot paths, decodes scope-check
paths, removes fragments and prevents equivalent sitemap-page duplicates. Query
URLs for package links are preserved as references, never crawled as expansions.

Each page and redirect destination is checked before a GET. Robots rules use
longest-match behavior (Allow wins a same-length tie) and user-agent group
selection. Explicit exclusions include all product/student/enrollment/teacher/API
routes, even if current robots allows a subpath. Off-domain targets are recorded
only. This scraper does not follow arbitrary links or submit any forms.

Raw HTML includes the public forms as originally served, but extracted knowledge
does not include operational values from them. Upcoming classroom batches and
enrollment/schedule controls are excluded; public static prerequisites and course
pricing remain. Contact links are harvested before footer removal.

Extraction is deterministic and tailored to this site's `data-pk-*`, `pp-facts`
and FAQ structures. Markup changes require selector review. FAQ answers and policy
paragraphs receive whitespace/punctuation spacing cleanup only, with no generative
paraphrasing. All exact duplicate facts retain original source records. Narrative
prices are evidence claims, not guessed package bindings.

No official regulatory sources are scraped in this phase. No authentication,
payments, enrollment or account access are performed.
