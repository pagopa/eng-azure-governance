---
name: local-azure-retirements
description: Use when converting an existing 02_azure_retirements_aggregate.tsv for a requested year and month into the canonical committee-ready 03_azure_retirements_slide.tsv, including deterministic projection, ordering, link fallback, diagnostics, and platform/subscription traceability.
---

# Local Azure Retirements

## When to use

- Convert an existing monthly aggregate TSV into the slide TSV.
- Rebuild or validate the slide projection without recollecting Azure data.
- Diagnose a deterministic aggregate-to-slide conversion failure.

## Boundary

- In scope: canonical slide-stage execution, deterministic field projection,
  sorting, fallback handling, diagnostics, and conversion checks.
- Out of scope: PowerPoint generation, narrative slide design, and source data recollection from Azure APIs.

## Workflow

1. Resolve the requested year and month. Do not silently select the newest
   export directory.
2. Confirm that
   `src/comitato/comitato_azure_retirements/exports/YYYY/MM/02_azure_retirements_aggregate.tsv`
   exists and contains data rows.
3. Read
   [references/slide-conversion-contract.md](references/slide-conversion-contract.md).
4. Run only the canonical slide stage. `schema-only` prevents live Azure
   collection while the slide stage reuses the existing aggregate:

   ```bash
   bash src/comitato/comitato_azure_retirements/run.sh \
     --mode schema-only \
     --workflow slide \
     --as-of-date YYYY-MM-DD
   ```

   Add `--output-root <root>` only when the aggregate lives below a different
   export root.
5. Inspect the generated slide TSV and the run diagnostics. Stop with the
   explicit diagnostic when the aggregate is missing, empty, or leaves a slide
   row without a traceable source link.

## Validation

- Require the exact ordered header defined in the reference.
- Confirm that every aggregate row was projected before canonical exact-row
  deduplication; do not manually filter unknown platforms.
- Confirm that `platforms_subscriptions_json` values are unchanged.
- Confirm that non-empty source links were preserved and empty links received
  the deterministic fallback.
- Confirm priority, date, technology or service, and feature ordering.
- Do not report success while slide-stage error diagnostics remain.
