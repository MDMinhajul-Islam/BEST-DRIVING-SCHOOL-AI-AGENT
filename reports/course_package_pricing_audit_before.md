# Course / package / pricing audit — before corrections

Audit date: 2026-09-13. Evidence: the 18 successful preserved public pages,
their cleaned blocks, services/courses/pricing/page metadata and the master file.
No remote collection or restricted route access was performed. Prices below are
verified against the saved snapshot, not a new live price check.

## Website versus extraction

The site has four service pages but five purchasable program families: Teen
Driver Education, Parent-Taught Log Driving Hours, Adult Online Education,
Adult Driving Lessons and Road Test. Six course pages provide 13 purchasable
options. Teen Driver Education contains two course pages and two packages;
their separate page headings do not make them unrelated programs.

| Website evidence | Existing extraction | Assessment |
| --- | --- | --- |
| Teen full: $399; 24 classroom, 7 driving, 7 observation; selector `data-badge="Best selling"` | Price/hours correct; canonical promotion null because course page lacks badge | Missing dedicated label aggregation |
| Teen BTW: $350; 7 driving, 7 observation; classroom completed elsewhere and learner license needed | Price/hours/prerequisites correct | No classroom inclusion; do not invent zero without explicit exclusion evidence |
| Adult 2/4/6/8/10 hours: $180/$246/$328/$405/$495 | Five options, correct prices and original prices | 10-hour promotion preserves Save $55 but hides Best selling in the same field |
| Adult online six-hour education: $19.99, crossed-out $70 | Correct distinct option, separate from six-hour driving lessons | Numeric canonical price and separate discount needed |
| PTDE 10/15/30 hours: $450/$675/$1,350; 30-hour Best selling | Correct three options; label mixed with promotion | Separate practice-hour semantics and label needed |
| Road test only/practice + test: $100/$140 | Correct two options and aliases | Shared course inclusions do not fully describe variant-specific practice |
| Repeated homepage/service/location cards | Consolidated into 13 IDs with observations | No accidental canonical duplication found |
| Online payment 3% non-refundable transaction processing charge | Preserved policy text, not base-price arithmetic | Separate structured fee needed |
| Upcoming batches and enrollment controls | Excluded from static knowledge | Correct; distinguish generic weekend statements from concrete dated batches |

## Data-model gaps documented before code changes

Existing `courses.json` actually contains package records with `course_name`,
opaque stable IDs, string prices, mixed `promotion`, and retained source
observations. There are no explicit program/course entities, readable package
aliases, independent marketing-label arrays or per-package booking handoff model.
These are modeling gaps, not evidence of missing purchasable options.

Minimal correction: add independent marketing labels to extraction/consolidation,
then rebuild from saved pages offline. Add a separate canonical catalog and
hierarchy with legacy IDs retained. Do not alter the official Phase B layer.
Backend field names, capacity, availability, taxes/deposits and cancellation
application remain unknown until authorized operational inspection.

The first offline rebuild exposed a validator compatibility defect: it assumes
every key named `sources` is a business-evidence array, but the Phase B
`regulatory_reference.sources` is a filename string. Correct the walker to
validate evidence arrays while leaving the separate regulatory reference intact.
