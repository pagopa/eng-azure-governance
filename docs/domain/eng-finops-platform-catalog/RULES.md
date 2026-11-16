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
- Remediation: Keep disabled and deleted entries in the catalog for lifecycle history, but exclude them from the mapping returned to runtime consumers.
- Rule: Catalog consumers must receive subscription-to-platform mappings only for entries whose state is `active`.

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
- Remediation: Replace guessed or sentinel dates with null, mark incomplete history explicitly, and provide evidence for every known date and interval.
- Rule: Real subscriptions must use nullable UTC lifecycle dates with matching sources and ordered, non-overlapping activity and platform-assignment intervals. Unknown history must not be interpreted as continuous activity or an unchanged platform. Complete histories must agree with creation, the latest disable date, deletion, and the current catalog mapping. A null-ID placeholder may have only null lifecycle metadata.
