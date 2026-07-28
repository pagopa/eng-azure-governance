# Slide Conversion Contract

This reference defines deterministic conversion rules from aggregate to slide TSV.

## Input file

- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/02_azure_retirements_aggregate.tsv`

## Output file

- `src/comitato/comitato_azure_retirements/exports/YYYY/MM/03_azure_retirements_slide.tsv`

## Ordered output schema

The output header must contain these columns in this exact order:

1. `technology_or_service`
2. `retiring_feature`
3. `platforms`
4. `platforms_subscriptions_json`
5. `priority_label`
6. `advice_type`
7. `action_required`
8. `retirement_date`
9. `source_links`

## Field mapping

| Slide field | Aggregate source | Rule |
| --- | --- | --- |
| `technology_or_service` | `technology_or_service` | Copy verbatim |
| `retiring_feature` | `retiring_feature` | Copy verbatim |
| `platforms` | `impacted_platforms` | Copy verbatim |
| `platforms_subscriptions_json` | `impacted_platforms_subscriptions_json` | Copy verbatim |
| `priority_label` | `priority_label` | Copy verbatim |
| `advice_type` | `advice_type` | Copy verbatim |
| `action_required` | `action_required`, `summary_text` | Use `action_required`; fallback to `summary_text` when empty, then remove XML tags and normalize whitespace |
| `retirement_date` | `retirement_date` | Copy verbatim |
| `source_links` | `source_links`, `source_identifiers` | Preserve non-empty `source_links`; otherwise apply the fallback rules below |

## Source link fallback

Split `source_identifiers` into non-empty identifiers, then convert each one:

1. Preserve an `http://` or `https://` identifier unchanged.
2. For an identifier starting with `/`, prepend
   `https://portal.azure.com/#resource` and URL-encode characters other than
   `/`.
3. For every other identifier, prepend
   `https://portal.azure.com/#search/` and URL-encode the complete identifier.
4. Remove duplicate links, sort case-insensitively, and join them with `, `.

## Ordering

Sort rows by:

1. Priority order: `Critico`, `Prioritario`, `Da pianificare`, `Debito`.
2. `retirement_date` ascending, with empty values last.
3. `technology_or_service` case-insensitive ascending.
4. `retiring_feature` case-insensitive ascending.

Unrecognized priority labels sort after the four known labels. Keep those rows
visible.

## Failure handling

- Missing `action_required`: use `summary_text` fallback.
- Missing `retirement_date`: keep row and preserve priority from aggregate.
- Unknown platform payloads: keep row unchanged.
- Missing `source_links`: derive from `source_identifiers`; fail conversion with an explicit diagnostic only when still empty.
- Missing aggregate input file: fail conversion with explicit path diagnostic.
- Empty aggregate input: fail conversion instead of emitting a successful empty slide.

## Completion checks

- The output header matches the ordered schema.
- Every input row is projected before exact duplicate slide rows are collapsed.
- `platforms_subscriptions_json` remains byte-for-byte unchanged per projected row.
- Sorting follows all four ordering keys.
- The slide-stage diagnostics contain no errors.
