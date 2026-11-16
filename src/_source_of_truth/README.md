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
- `state` must be `active`, `disabled`, or `deleted`.
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

For a real subscription, the metadata contains:

- `purchased_on`: the verified purchase calendar day as a quoted `YYYY-MM-DD`
  string, or `null` when unknown. It does not assert a creation instant.
- `created_at`: the Azure subscription creation instant, or `null` when unknown.
- `disabled_at`: the most recent verified disactivation instant, or `null` when
  not established. It is not necessarily the end of the subscription's life:
  reactivation is possible.
- `deleted_at`: the verified deletion instant, or `null` when not established.
- `date_sources`: one non-empty evidence reference for each non-null date,
  including `purchased_on`, keyed by its field name. Unknown dates must not have
  a source.
- `history_complete`: whether both activity and platform-assignment histories
  are complete. It must be `false` when earlier events are missing.
- `incomplete_reason`: a non-empty explanation when history is incomplete,
  otherwise `null`.
- `activity_periods`: verified activity intervals, including separate intervals
  after reactivation. Each contains `started_at`, `ended_at`, and `source`.
- `platform_assignments`: verified platform-association intervals. Each contains
  `platform`, `started_at`, `ended_at`, and `source`. This history is independent
  of activity: an association can continue while a subscription is disabled.

Timestamps must be quoted ISO 8601 UTC strings, for example
`"2026-10-01T09:30:00Z"`, with at most six fractional-second digits.
Calendar dates and timezone-free timestamps are rejected for the instant fields;
`purchased_on` deliberately preserves day-only precision.
Intervals are ordered, non-overlapping, and half-open: the start is included,
the end is excluded. A null `ended_at` means an ongoing verified interval,
**not an unknown end date**. Do not insert an interval when its bounds cannot
be established; keep the history incomplete instead. The null-ID `Unassigned`
placeholder has `lifecycle: null`: it is not an Azure subscription.

For a historical instant, intersect the activity intervals with the association
intervals for the requested platform. When `history_complete: false`, verified
intervals provide partial evidence only. Missing intervals or null lifecycle
dates mean **unknown**, not "always active", "never active", or "never disabled".
Without complete coverage, the catalog cannot provide an exhaustive historical
list; callers must report that uncertainty rather than silently exclude records.
Do not infer the initial platform from the current grouping.

### Evidence and old subscriptions

Use authoritative creation, cancellation, reactivation, deletion, and approved
platform-assignment records. Keep their references in `date_sources` or the
interval's `source`. Never substitute a Git commit, first resource creation,
first cost, purchase date, or enrollment-account start date for subscription
creation. Reject Azure sentinel dates such as `0001-01-01`.

The initial enrichment was checked against Azure billing APIs and available
subscription-level activity logs on 2026-11-03. Azure activity logs normally
retain only 90 days unless exported. Absence from those logs does not establish
that an older event never occurred. Archived logs or authoritative exports may
be needed to fill gaps; preserve unknown dates and incomplete history until
such evidence becomes available.

The user-supplied Azure portal Properties screenshot establishes ORG's purchase
day as `2021-07-02` (displayed as `02/07/2021`). The billing API returned a sentinel
for this same subscription. Preserve the portal evidence in `purchased_on`;
do not replace `created_at` with an invented midnight timestamp. No actual
creation, disactivation, or deletion instants were recovered during the initial
check. Activity queries succeeded for 60 subscriptions; the other seven
identified subscriptions returned `SubscriptionNotFound`, not evidence of a
specific deletion date.

## Consumers and validation

The runtime reads and validates the catalog through `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`.

Run the focused catalog tests after changing either the schema reader or the catalog:

```bash
src/comitato/comitato_azure_retirements_v2/.venv/bin/python -m pytest -q tests/comitato/comitato_azure_retirements_v2/adapters/test_platform_catalog_yaml.py
```
