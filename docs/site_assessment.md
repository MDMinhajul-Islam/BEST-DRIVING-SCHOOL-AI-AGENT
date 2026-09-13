# Phase 1 — HTML assessment

Inspected the repository and live public site before implementation on 2026-09-13.
The workspace was empty and was not a Git repository. A local virtual environment
was created; no existing application or environment conventions were replaced.

The live sitemap is a namespaced XML `urlset` with 18 URLs and `lastmod` values.
Robots is available and restricts operational routes. The implementation will
also exclude all student, enrollment, product, login, teacher and API routes
explicitly, including any such links present on public pages.

Representative pages inspected: homepage, adult service, adult driving course,
FAQ, Allen location, terms, sitemap and robots. All returned HTTP 200 through
requests. Content is server-rendered within `main`. Navigation, footer and cookie
consent are outside it or identifiable by attributes. No Selenium is needed.

Package selectors use `data-pk-chip`, `data-value`, `data-price`, `data-was`,
`data-meta`, `data-note` and, on service/location pages, `data-link`. The course
pages expose matching selectors with `data-enroll-chip`. These attributes must
be extracted before removing form controls; default displayed price alone would
miss non-default packages and original prices. Hidden FAQ panels are public
content (`data-faq-panel`) paired with questions in their containing item.

Course pages contain enrollment forms and date/time controls. Do not submit
forms, fetch their action routes, or treat embedded scheduling fields as
availability. Preserve public course descriptions and `pp-facts` requirements.

Use ordered heading/paragraph/list/table blocks plus explicit selector-package
blocks rather than a flat text dump. Harvest public contacts separately before
removing repeated layout. Preserve policy sections verbatim after whitespace
cleanup. Location pages can describe a service area whose training/test office
is in Plano; an address mentioned there must not become an invented Allen office.

School licensing statements will carry an official-verification flag. Prices,
policies and prerequisite wording require source attribution and conflict review.
