# AI Architecture Contract v1.1.0

## Repository

`eng-azure-governance` manages Azure governance policy definitions, policy assignments, custom roles, policy remediation support, Terraform lock handling, and operational governance automation.

## Purpose

The repository is an Azure Policy and governance infrastructure repository. It organizes policy families into Terraform roots and scripts, then applies or remediates governance state through workflows.

## System Boundaries

In scope:

- Custom roles under `src/01_custom_roles/`.
- Policy definition families under `src/02_policy_*` directories.
- Policy sets under `src/03_policy_set/`.
- Policy assignments and environments under `src/04_policy_assignments/`.
- Policy remediation and container app job graph scripts under `src/scripts/`.
- Repository workflow automation under `.github/workflows/`.

Out of scope:

- Azure and Azure DevOps access assignments handled by `eng-azure-authorization`.
- Application resource deployment outside governance controls.
- Non-Azure policy-as-code.

## Main Components

| Component | Path | Responsibility |
| --- | --- | --- |
| Custom roles | `src/01_custom_roles/` | Azure custom role definitions. |
| Policy definitions | `src/02_policy_*` | Domain-specific Azure Policy definitions and `policy_rules/`. |
| Policy sets | `src/03_policy_set/` | Grouped policy initiatives. |
| Assignments | `src/04_policy_assignments/` | Environment-specific policy assignment wiring. |
| Remediation scripts | `src/scripts/policy_remediation.sh` | Policy remediation operations. |
| Container app job graph | `src/scripts/update_container_app_job_graph.sh` | Supporting governance automation. |
| Workflows | `.github/workflows/` | Pre-commit, static analysis, release, drift, remediation, and automation workflows. |

## Architecture Flow

```text
Policy definitions and custom roles
  -> policy sets and assignments
  -> Terraform wrappers per policy family
  -> CI/CD validation and drift/remediation workflows
  -> Azure governance state
```

The repository is policy-family oriented. Each `src/02_policy_*` directory owns a focused policy domain, and assignments are separated from definition roots.

## Validation Surface

Observed validation surfaces include:

- `Makefile` targets: `format`, `lint`, and `lock`.
- Workflows for pre-commit, static analysis, release, policy remediation, Terraform drift, PR title checks, and container app job automation.
- Terraform wrapper scripts under policy directories and `.identity/`.
- `CONTRIBUTING.md` and `SECURITY.md`.

No test files were observed under `tests/` in the current workspace structure.

## Operational Notes

- Keep policy definitions, policy sets, and assignments separate.
- Do not mix authorization assignments into policy governance changes.
- Treat policy weakening or remediation behavior changes as high-review operations.
- Preserve lockfile/platform conventions when providers change.

## Risks And Open Questions

| Risk | Current evidence | Recommended handling |
| --- | --- | --- |
| No test directory observed | `tests/` not present in workspace listing for this repo. | Add lightweight validation tests or script checks around policy generation and remediation logic when changed. |
| Many policy family roots | Multiple `src/02_policy_*` directories exist. | Keep naming and wrapper conventions consistent across policy families. |
| Remediation workflow blast radius | `policy_remediation.yml` and remediation script exist. | Require explicit target scope and dry-run review where possible. |

## Contract Status

This repository is ready for AI Architecture Contract v1.1.0 as an Azure governance policy repository. The contract should be revisited when executable tests or policy-family generation are added.
