---
name: local-azure-retirements
description: Use when converting an existing 02_azure_retirements_aggregate.tsv for a requested year and month into the canonical committee-ready 03_azure_retirements_slide.tsv, including deterministic projection, ordering, link fallback, diagnostics, and platform/subscription traceability.
---

# Local Azure Retirements

## When to use

- Convert an existing monthly aggregate TSV into the slide TSV.
- Rebuild or validate the slide projection for a given month.
- Diagnose a deterministic aggregate-to-slide conversion failure.

## Boundary

- In scope: canonical slide-stage execution through the v2 `slides` report,
  deterministic field projection, sorting, fallback handling, diagnostics, and
  conversion checks.
- Out of scope: PowerPoint generation, narrative slide design, and hand-editing
  exported TSV files.
- Constraint: the v2 `slides` report runs its dependency closure, which
  includes live Azure acquisition. v2 has no slide-only mode. Offline replay
  requires a replay bundle with saved inputs; historical schema-1 bundles cannot
  be replayed.

## Workflow

1. Resolve the requested year and month. Do not silently select the newest
   export directory.
2. Confirm that
   `src/comitato/comitato_azure_retirements_v2/exports/YYYY/MM/02_azure_retirements_aggregate.tsv`
   exists and contains data rows.
3. Read
   [references/slide-conversion-contract.md](references/slide-conversion-contract.md).
4. Run the v2 `slides` report for the same as-of date. Pass the subscription
   scope the aggregate was built from. Use `--output-path <root>` only when the
   aggregate lives below a different export root:

   ```bash
   bash src/comitato/comitato_azure_retirements_v2/run.sh \
     --report slides \
     --subscriptions <sub-id-1,sub-id-2> \
     --as-of-date YYYY-MM-DD \
     --catalog-path src/_source_of_truth/eng-finops-platforms.yaml \
     --output-format json
   ```

   The run recomputes the aggregate dependency closure. Confirm the aggregate
   is unchanged or explain the difference before accepting the slide output.
5. Inspect the generated `03_azure_retirements_slide.tsv`,
   `publication-manifest.json`, and the JSON run diagnostics. Stop with the
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
