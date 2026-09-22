# Azure Governance Rules

These rules govern changes to the policy, role, initiative, assignment, and remediation artifacts in this repository.

## GOV-001 - Preserve apply order

- Rule ID: GOV-001
- Owner: Azure Governance
- Severity: warning
- Enforcement owner: not enforced
- Evidence: `README.md`, `.github/PULL_REQUEST_TEMPLATE.md`
- Remediation: Review the numbered `src/` stages and document any intentional sequencing change before merge.
- Rule: Changes must preserve or explicitly account for the `01` through `04` apply sequence.

## GOV-002 - Scope custom roles narrowly

- Rule ID: GOV-002
- Owner: Azure Governance
- Severity: blocking
- Enforcement owner: not enforced
- Evidence: `README.md`, `.github/security-baseline.md`, `.github/instructions/internal-terraform.instructions.md`
- Remediation: Reduce permissions and target scope to the narrowest effective governance responsibility, or record an evidence-backed exception.
- Rule: Custom RBAC roles must follow the least-privilege principle.

## GOV-003 - Document high-impact policy effects

- Rule ID: GOV-003
- Owner: Azure Governance
- Severity: blocking
- Enforcement owner: not enforced
- Evidence: `.github/PULL_REQUEST_TEMPLATE.md`, `.github/security-baseline.md`
- Remediation: Add the affected scope, policy effect, blast radius, exemption impact, and rollback strategy to the change record.
- Rule: Changes with high-impact policy effects must document their governance impact before merge.

## GOV-004 - Keep validation non-mutating

- Rule ID: GOV-004
- Owner: Azure Governance
- Severity: blocking
- Enforcement owner: `.github/workflows/_pre-commit.yml`
- Evidence: `.github/workflows/_pre-commit.yml`, `.pre-commit-config.yaml`
- Remediation: Run Terraform validation with the repository's backend-disabled and lockfile-readonly settings.
- Rule: Local Terraform validation must not reach or mutate a remote backend.
