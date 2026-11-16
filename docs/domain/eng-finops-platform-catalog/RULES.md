# Eng FinOps Platform Catalog Rules

These rules govern the canonical mapping of Eng FinOps platforms to Azure subscriptions.

## CAT-001 - Preserve the version 1 shape

- Rule ID: CAT-001
- Serves: PUR
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`, `tests/comitato/comitato_azure_retirements_v2/adapters/test_platform_catalog_yaml.py`
- Evidence: `src/_source_of_truth/README.md`, `src/_source_of_truth/eng-finops-platforms.yaml`
- Remediation: Restore the supported version 1 fields, or change the reader and tests through an explicit schema decision.
- Rule: The catalog root must contain only `schema_version: 1` and `platforms`, with optional `tenant_id`; each platform must contain only `subscriptions`, and each subscription must contain `name`, `id`, and `state`, with optional `lifecycle` as defined in `src/_source_of_truth/README.md`. The additive lifecycle extension must preserve legacy entries and current runtime mappings.

## CAT-002 - Validate subscription identifiers

- Rule ID: CAT-002
- Serves: PUR
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`, `tests/comitato/comitato_azure_retirements_v2/adapters/test_platform_catalog_yaml.py`
- Evidence: `src/_source_of_truth/README.md`, `src/_source_of_truth/eng-finops-platforms.yaml`
- Remediation: Replace malformed or duplicate identifiers and provide an identifier for every active subscription.
- Rule: Every non-null subscription ID must be a valid, unique UUID, and an active subscription must not have a null ID.

## CAT-003 - Keep active subscription names unique

- Rule ID: CAT-003
- Serves: PUR
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`, `tests/comitato/comitato_azure_retirements_v2/adapters/test_platform_catalog_yaml.py`
- Evidence: `src/_source_of_truth/README.md`, `src/_source_of_truth/eng-finops-platforms.yaml`
- Remediation: Rename or reclassify colliding active entries so their normalized names are unique.
- Rule: Active subscription names must be unique after trimming, lowercasing, and collapsing repeated whitespace.

## CAT-004 - Expose active mappings only

- Rule ID: CAT-004
- Serves: PRI-03
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`, `tests/comitato/comitato_azure_retirements_v2/adapters/test_platform_catalog_yaml.py`
- Evidence: `src/_source_of_truth/README.md`, `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`
- Remediation: Keep dismissed entries in the catalog with their known lifecycle dates, but exclude them from the mapping returned to runtime consumers.
- Rule: Subscription state must be `active` or `dismiss`. Catalog consumers must receive subscription-to-platform mappings only for entries whose state is `active`.

## CAT-005 - Match by the runtime's declared key

- Rule ID: CAT-005
- Serves: PRI-03
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements_v2/retirements/application/orchestration.py`
- Evidence: [ADR-0003](../../adr/0003-catalog-matching-keys.md), `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`
- Remediation: Restore the runtime's declared key, or record a new decision before changing it.
- Rule: The runtime matches catalog entries by subscription ID.

## CAT-006 - Validate catalog tenant identifier

- Rule ID: CAT-006
- Serves: PUR
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`, `tests/comitato/comitato_azure_retirements_v2/adapters/test_platform_catalog_yaml.py`
- Evidence: `src/_source_of_truth/README.md`, `src/_source_of_truth/eng-finops-platforms.yaml`
- Remediation: Correct the tenant UUID or omit the optional field for a legacy schema-version-1 catalog.
- Rule: When present, the root `tenant_id` must be a valid UUID.

## CAT-007 - Preserve lifecycle uncertainty

- Rule ID: CAT-007
- Serves: PUR
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements_v2/retirements/adapters/filesystem/platform_catalog_yaml.py`, `tests/comitato/comitato_azure_retirements_v2/adapters/test_platform_catalog_yaml.py`
- Evidence: `src/_source_of_truth/README.md`, `src/_source_of_truth/eng-finops-platforms.yaml`
- Remediation: Replace guessed or sentinel dates with null and use only the three lifecycle fields declared by the canonical YAML.
- Rule: A lifecycle block must contain exactly `created_at`, `disabled_at`, and `deleted_at`, each a quoted `YYYY-MM-DD` date or null. `created_at` records the enrollment-account association start, not a certified Azure creation date. Known dates must be ordered; active entries must have null disable and deletion dates. Unknown dates must not be interpreted as continuous activity or an unchanged platform. A null-ID placeholder may have either the same block or null lifecycle metadata; a real subscription must not have null lifecycle metadata when the field is present.
