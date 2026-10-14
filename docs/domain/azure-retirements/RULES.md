# Azure Retirement Intelligence Rules

These rules govern the v2 retirement runtime and its committee-facing artifacts.

## RET-001 - Require live scope

- Rule ID: RET-001
- Serves: PRI-04
- Owner: Azure Retirement Intelligence
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements_v2/retirements/adapters/azure/subscription_api.py`
- Evidence: `src/comitato/comitato_azure_retirements_v2/README.md`, `src/comitato/comitato_azure_retirements_v2/retirements/adapters/azure/subscription_api.py`
- Remediation: Supply subscriptions or management groups before running in live mode.
- Rule: Live collection must refuse an empty Azure scope.

## RET-002 - Use source-backed resource resolution

- Rule ID: RET-002
- Serves: PRI-03
- Owner: Azure Retirement Intelligence
- Severity: blocking
- Enforcement owner: `.github/workflows/_code-analysis.yml`, which runs `tests/comitato/comitato_azure_retirements_v2`
- Evidence: `src/comitato/comitato_azure_retirements_v2/README.md`, `tests/comitato/comitato_azure_retirements_v2/reports/test_service_health.py`
- Remediation: Preserve the event with explicit unavailable fields and diagnostics when no Azure-published resource evidence exists.
- Rule: A runtime must not infer resource-level impact or synthesize missing values from names, regions, service labels, or similarity.

## RET-003 - Keep runtime outputs outside version control

- Rule ID: RET-003
- Serves: PUR
- Owner: Azure Retirement Intelligence
- Severity: warning
- Enforcement owner: not enforced
- Evidence: `src/comitato/comitato_azure_retirements_v2/README.md`
- Remediation: Keep export artifacts out of commits and use `tmp/` for local review snapshots; sanitize any fixture before tracking it.
- Rule: Generated retirement exports and runtime diagnostics must remain untracked unless a sanitized fixture is intentionally documented.

## RET-004 - Preserve canonical output contracts

- Rule ID: RET-004
- Serves: PUR
- Owner: Azure Retirement Intelligence
- Severity: blocking
- Enforcement owner: `.github/workflows/_code-analysis.yml`, which runs the v2 contract tests
- Evidence: `src/comitato/comitato_azure_retirements_v2/README.md`, `tests/comitato/comitato_azure_retirements_v2`
- Remediation: Update the runtime and its tests together, keeping the required filenames and ordered headers explicit.
- Rule: The runtime's raw, aggregate, slide, diagnostics, and manifest artifacts must preserve their documented contracts.

## RET-006 - Publish monthly bundles atomically

- Rule ID: RET-006
- Serves: PRI-04
- Owner: Azure Retirement Intelligence
- Severity: blocking
- Enforcement owner: `tests/comitato/comitato_azure_retirements_v2/adapters/test_filesystem_publication.py`, run by `.github/workflows/_code-analysis.yml`
- Evidence: `src/comitato/comitato_azure_retirements_v2/README.md`, `tests/comitato/comitato_azure_retirements_v2/adapters/test_filesystem_publication.py`
- Remediation: Stage and validate the new bundle before it replaces the month, and return a non-zero status without touching the current bundle on failure.
- Rule: In the v2 runtime, a failed run leaves the current monthly bundle unchanged, and a successful run replaces it whole.
