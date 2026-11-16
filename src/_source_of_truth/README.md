# Eng FinOps platform catalog

`eng-finops-platforms.yaml` is the canonical mapping of Eng FinOps platforms
to Azure subscriptions.

The [domain glossary](../../docs/domain/eng-finops-platform-catalog/GLOSSARY.md) defines the catalog vocabulary and its [rules](../../docs/domain/eng-finops-platform-catalog/RULES.md). The repository [architecture](../../docs/architecture.md) records the catalog-to-runtime dependency.

No diagram is provided because this component has one material downstream relationship, already shown in the repository architecture.

## Catalog contract

- The root contains `schema_version: 1` and `platforms`, with an optional
  `tenant_id` UUID. The canonical catalog includes this tenant ID.
- Each platform contains `subscriptions`, which may be empty.
- Each subscription contains `name`, `id`, and `state`, with optional
  `lifecycle` metadata. The canonical catalog includes it for every record.
- `state` must be `active` or `dismiss`. The former `disabled` and `deleted`
  states are replaced by `dismiss`; their dates remain in `lifecycle`.
- Non-null IDs must be valid and unique UUIDs.
- A null ID is allowed only when the subscription is not active.
- Active subscription names must be unique after trimming, lowercasing, and
  collapsing repeated whitespace.

The Azure retirements runtime uses only entries with `state: active` and maps
subscription IDs, as recorded in
[ADR-0003](../../docs/adr/0003-catalog-matching-keys.md). Unsupported or
malformed schemas stop processing with an explicit error. When `tenant_id` is
present, the reader validates it as a UUID; it remains catalog metadata and
does not change subscription matching or runtime scope. Older schema-version-1
catalogs without `tenant_id` remain supported.

## Subscription lifecycle history

`lifecycle` is an additive schema-version-1 extension. Legacy entries without it
remain supported. Retirement consumers still use the current `state`; they do
not automatically select historical mappings.

When present, the metadata must contain exactly three keys:

```yaml
lifecycle:
  created_at: "2019-12-18"
  disabled_at: null
  deleted_at: null
```

- `created_at`: the enrollment-account association start day
  (`enrollmentAccountStartDate`), as declared by the canonical YAML. It is not a
  certified Azure subscription creation date.
- `disabled_at`: the disactivation calendar day, or `null` when unknown.
- `deleted_at`: the deletion calendar day, or `null` when unknown.

All three values must be quoted ISO calendar dates (`YYYY-MM-DD`) or `null`.
Timestamps, unquoted YAML dates, invalid calendar days, and Azure sentinel dates
such as `0001-01-01` are rejected. The known dates must follow
`created_at <= disabled_at <= deleted_at`, ignoring unknown values. Equal dates
are allowed. An `active` entry must have null `disabled_at` and `deleted_at`.
A `dismiss` entry is excluded from current runtime mappings even when some
dates are unknown.

The null-ID `Unassigned` placeholder may have the same three-key block.
`lifecycle: null` remains supported only for null-ID placeholders, not real
subscriptions. A null ID is still forbidden for an `active` entry.

The old purchase, provenance, completeness, activity-interval, and
platform-assignment fields are not part of this contract and are rejected.
These three dates do not provide reactivation or platform-transfer histories.
Unknown dates must stay null; they do not prove continuous activity or an
unchanged platform. Do not infer dates from first costs, resource ages, or Git
history.

The owner assigned `disabled_at: "2026-03-30"` and
`deleted_at: "2026-06-30"` to the entries previously marked `disabled`, including
`Unassigned`. Existing dates for entries previously marked `deleted` are
preserved. These assignments are not evidence recovered from Azure.

The PDA-Migration-PostgreSQL date remains unknown. On 2026-11-16, the subscription
API exposed no creation metadata, the retained subscription-level activity log
contained no events, and the billing-subscription date query returned
`Forbidden`. A verified billing export or suitable billing read permission is
needed before filling this value.

## Consumers and validation

The runtime reads and validates the catalog through `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`.

Run the focused catalog tests after changing either the schema reader or the catalog:

```bash
.venv/bin/python -m pytest -q tests/comitato/comitato_azure_retirements_v2/adapters/test_platform_catalog_yaml.py
```
