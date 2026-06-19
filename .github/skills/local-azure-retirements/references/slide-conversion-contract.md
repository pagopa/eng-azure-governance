# Slide Conversion Contract

This reference defines deterministic conversion rules from aggregate to slide TSV.

## Input file

- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/02_azure_retirements_aggregate.tsv`

## Output file

- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/03_azure_retirements_slide.tsv`

## Field mapping

| Slide field | Aggregate source | Rule |
| --- | --- | --- |
| `priority_label` | `priority_label` | Copy verbatim |
| `retiring_feature` | `retiring_feature` | Copy verbatim |
| `action_required` | `action_required`, `summary_text` | Use `action_required`; fallback to `summary_text` when empty |
| `retirement_date` | `retirement_date` | Copy verbatim |
| `platforms` | `impacted_platforms` | Copy verbatim |
| `platforms_subscriptions_json` | `impacted_platforms_subscriptions_json` | Copy verbatim |
| `advice_type` | `advice_type` | Copy verbatim |
| `source_links` | `source_links` | Copy verbatim |

## Ordering

Sort rows by:

1. Priority order: `Critico`, `Prioritario`, `Da pianificare`, `Debito`.
2. `retirement_date` ascending, with empty values last.
3. `retiring_feature` case-insensitive ascending.

## Failure handling

- Missing `action_required`: use `summary_text` fallback.
- Missing `retirement_date`: keep row and preserve priority from aggregate.
- Unknown platform payloads: keep row unchanged.
- Missing aggregate input file: fail conversion with explicit path diagnostic.
