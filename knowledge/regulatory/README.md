# Official Texas regulatory knowledge

Regulatory research date: 2026-09-13

General Class C guidance. Use only records marked `official_verified` for general answers; flagged details require confirmation. Source dates are not assumed effective dates.

Separate structured layer: `data/structured/texas_regulatory_knowledge.json`. The master business file contains an additive `regulatory_reference`; existing school evidence remains business-only.

Rebuild offline: `.venv/Scripts/python.exe -m src.regulatory`. Refresh public originals: `python -m src.regulatory_collect`, then review changed sources and curate rules before rebuilding. A refresh does not approve changed rules automatically. Review [unresolved questions](unresolved_questions.md) and [manual review](../../reports/phase_b_manual_review.md).

READY pathways support general explanation only. Adult permits, provider-specific TPST admission, foreign licensing and flagged details are not approved for automatic qualification or booking. Retell remains manually configured later.
