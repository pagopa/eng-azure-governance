# Azure Retirement Intelligence Rules

These rules govern the retirement evidence exporter and its committee-facing artifacts.

## RET-001 - Require live scope

- Rule ID: RET-001
- Owner: Azure Retirement Intelligence
- Severity: blocking
- Enforcement owner: `src/comitato/comitato_azure_retirements/libs/config.py`
- Evidence: `src/comitato/comitato_azure_retirements/README.md`, `src/comitato/comitato_azure_retirements/libs/config.py`, `tests/comitato/comitato_azure_retirements`
- Remediation: Supply subscriptions or management groups before running in live mode.
- Rule: Live collection must refuse an empty Azure scope.

## RET-002 - Use source-backed resource resolution

- Rule ID: RET-002
- Owner: Azure Retirement Intelligence
- Severity: blocking
- Enforcement owner: `tests/comitato/comitato_azure_retirements`
- Evidence: `src/comitato/comitato_azure_retirements/README.md`, `docs/comitato-azure-retirements-runtime.md`, `tests/comitato/comitato_azure_retirements`
- Remediation: Preserve the event with explicit unavailable fields and diagnostics when no Azure-published resource evidence exists.
- Rule: The exporter must not infer resource-level impact from names, regions, service labels, or similarity.

## RET-003 - Keep runtime outputs outside version control

- Rule ID: RET-003
- Owner: Azure Retirement Intelligence
- Severity: warning
- Enforcement owner: not enforced
- Evidence: `src/comitato/comitato_azure_retirements/README.md`, `docs/comitato-azure-retirements-runtime.md`, `.gitignore`
- Remediation: Use the ignored export path for runtime output and `tmp/` for local review snapshots; sanitize any fixture before tracking it.
- Rule: Generated retirement exports and runtime diagnostics must remain untracked unless a sanitized fixture is intentionally documented.

## RET-004 - Preserve canonical output contracts

- Rule ID: RET-004
- Owner: Azure Retirement Intelligence
- Severity: blocking
- Enforcement owner: `.github/workflows/_code-analysis.yml`
- Evidence: `src/comitato/comitato_azure_retirements/README.md`, `docs/comitato-azure-retirements-runtime.md`, `tests/comitato/comitato_azure_retirements`, `.github/workflows/_code-analysis.yml`
- Remediation: Update the exporter and its tests together, keeping the required filenames and ordered headers explicit.
- Rule: Raw, aggregate, slide, diagnostics, and manifest artifacts must preserve their documented contracts.

## RET-005 - Make degradation explicit

- Rule ID: RET-005
- Owner: Azure Retirement Intelligence
- Severity: blocking
- Enforcement owner: `tests/comitato/comitato_azure_retirements`
- Evidence: `docs/comitato-azure-retirements-runtime.md`, `src/comitato/comitato_azure_retirements/README.md`, `tests/comitato/comitato_azure_retirements`
- Remediation: Record bounded failures or truncation in diagnostics and the run manifest; do not silently convert partial evidence into a clean run.
- Rule: Degraded collection is valid only when explicitly enabled and visibly reported.
