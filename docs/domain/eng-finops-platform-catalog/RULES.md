# Eng FinOps Platform Catalog Rules

These rules govern the canonical mapping of Eng FinOps platforms to Azure subscriptions.

## CAT-001 - Preserve the version 1 shape

- Rule ID: CAT-001
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements/libs/platform_catalog.py`, `tests/comitato/comitato_azure_retirements/test_platform_catalog.py`
- Evidence: `src/_source_of_truth/README.md`, `src/_source_of_truth/eng-finops-platforms.yaml`
- Remediation: Restore the exact version 1 root and entry fields, or change the reader and tests through an explicit schema decision.
- Rule: The catalog root must contain only `schema_version: 1` and `platforms`; each platform must contain only `subscriptions`, and each subscription must contain only `name`, `id`, and `state`.

## CAT-002 - Validate subscription identifiers

- Rule ID: CAT-002
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements/libs/platform_catalog.py`, `tests/comitato/comitato_azure_retirements/test_platform_catalog.py`
- Evidence: `src/_source_of_truth/README.md`, `src/_source_of_truth/eng-finops-platforms.yaml`
- Remediation: Replace malformed or duplicate identifiers and provide an identifier for every active subscription.
- Rule: Every non-null subscription ID must be a valid, unique UUID, and an active subscription must not have a null ID.

## CAT-003 - Keep active subscription names unique

- Rule ID: CAT-003
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements/libs/platform_catalog.py`, `tests/comitato/comitato_azure_retirements/test_platform_catalog.py`
- Evidence: `src/_source_of_truth/README.md`, `src/_source_of_truth/eng-finops-platforms.yaml`
- Remediation: Rename or reclassify colliding active entries so their normalized names are unique.
- Rule: Active subscription names must be unique after trimming, lowercasing, and collapsing repeated whitespace.

## CAT-004 - Expose active mappings only

- Rule ID: CAT-004
- Owner: Eng FinOps Platform Catalog
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements/libs/platform_catalog.py`, `tests/comitato/comitato_azure_retirements/test_platform_catalog.py`
- Evidence: `src/_source_of_truth/README.md`, `src/comitato/comitato_azure_retirements/libs/runtime_runner.py`
- Remediation: Keep disabled and deleted entries in the catalog for lifecycle history, but exclude them from the mapping returned to runtime consumers.
- Rule: Catalog consumers must receive subscription-to-platform mappings only for entries whose state is `active`.
