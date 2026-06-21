---
name: local-azure-retirements
description: Use when converting Azure retirements aggregate TSV data into committee-ready slide TSV rows with deterministic field mapping, priority labeling, and platform/subscription traceability.
---

# Local Azure Retirements

Use this skill when the operator needs controlled support for aggregate-to-slide conversions in the Azure retirements workflow.

## When to use

- The input is `02_azure_retirements_aggregate.tsv`.
- The expected output is `03_azure_retirements_slide.tsv`.
- The request needs deterministic mapping, not free-form summarization.

## Boundary

- In scope: deterministic field projection, sorting, fallback handling, and conversion checks.
- Out of scope: PowerPoint generation, narrative slide design, and source data recollection from Azure APIs.

## Required conversion posture

- Preserve one output row per aggregate row.
- Keep `platforms_subscriptions_json` payloads unchanged from aggregate input.
- Keep source links traceable and never drop non-empty links.
- When `source_links` is empty, derive deterministic fallback links from aggregate `source_identifiers`.
- Use `summary_text` as fallback only when `action_required` is empty.

## Validation expectations

- Output includes exactly these columns:
  `platforms`, `platforms_subscriptions_json`, `priority_label`, `advice_type`, `technology_or_service`, `retiring_feature`, `action_required`, `retirement_date`, `source_links`.
- Sorting follows priority then retirement date then feature name.
- Unknown platform rows stay visible and are not filtered.

## Reference

Use [references/slide-conversion-contract.md](references/slide-conversion-contract.md) for detailed mapping tables and failure handling patterns.
