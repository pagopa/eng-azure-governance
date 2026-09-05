# ADR-0001: Use a four-domain repository context map

* Status: accepted
* Date: 2026-09-01
* Deciders: User through delegated bootstrap approval
* Related: [Context map](../../CONTEXT-MAP.md), [architecture](../architecture.md), [domain documentation](../agents/domain.md)

## Context and Problem Statement

The repository's local agent documentation declared a single-context layout, but the repository contains four durable responsibility areas with separate vocabulary, state, schema, or execution lifecycles. A single glossary would merge policy controls, workload identity, the Eng FinOps subscription catalog, and retirement evidence.

## Domain Evidence

The closed promotion test is applied to each candidate area below. `Yes` verdicts form the recorded count; size is not used as a signal.

### Azure Governance

| Signal | Verdict | Evidence |
| --- | --- | --- |
| Same word means different things inside and outside | Yes | `src/04_policy_assignments/` binds policies, while `.identity/02_identity_prod_auth.tf` assigns RBAC roles. |
| Represented differently from neighbouring areas | Yes | `src/02_policy_api_management/`, `src/03_policy_set/`, `src/04_policy_assignments/` |
| Serves a different audience | Not evidenced | Repository ownership is shared and no separate audience contract is checked in. |
| Uses a different tool set | No | Azure Governance and Identity both use Terraform and AzureRM. |
| Lives in a separate code base, state file, or schema | Yes | `src/01_custom_roles/backend.ini`, `src/03_policy_set/backend.ini`, `src/04_policy_assignments/env/org/backend.tfvars` |
| Follows a separate delivery process | Yes | `README.md`, `CONTRIBUTING.md`, `.github/workflows/terraform_drift.yml` |
| Can be delivered independently | Yes | Numbered roots own separate wrappers and backend configuration. |
| Another area depends on it directionally | Yes | `.identity/02_identity_prod_auth.tf` references roles defined in `src/01_custom_roles/`. |

Recorded count: 6.

### Identity

| Signal | Verdict | Evidence |
| --- | --- | --- |
| Same word means different things inside and outside | Yes | `.identity/02_identity_prod_auth.tf` assigns roles, while `src/04_policy_assignments/` assigns policies. |
| Represented differently from neighbouring areas | Yes | `.identity/02_identity_prod.tf`, `.identity/02_identity_prod_auth.tf` |
| Serves a different audience | Not evidenced | No separate audience contract is checked in. |
| Uses a different tool set | No | Identity and Azure Governance both use Terraform and AzureRM. |
| Lives in a separate code base, state file, or schema | Yes | `.identity/env/prod/backend.tfvars` |
| Follows a separate delivery process | Yes | `.identity/terraform.sh` is outside the numbered governance apply flow. |
| Can be delivered independently | Yes | `.identity/` is a standalone Terraform root with its own backend and variables. |
| Another area depends on it directionally | Yes | Identity grants depend on role names defined by Azure Governance. |

Recorded count: 6.

### Eng FinOps Platform Catalog

| Signal | Verdict | Evidence |
| --- | --- | --- |
| Same word means different things inside and outside | Yes | `state` is a subscription lifecycle field in `src/_source_of_truth/eng-finops-platforms.yaml`, not Terraform backend state. |
| Represented differently from neighbouring areas | Yes | `src/_source_of_truth/eng-finops-platforms.yaml` is a versioned mapping rather than Terraform or runtime output. |
| Serves a different audience | Not evidenced | The catalog names Eng FinOps platforms, but no separate maintainer audience is declared. |
| Uses a different tool set | Yes | YAML source plus `src/comitato/comitato_azure_retirements/libs/platform_catalog.py` |
| Lives in a separate code base, state file, or schema | Yes | `src/_source_of_truth/README.md` defines schema version 1. |
| Follows a separate delivery process | Not evidenced | The catalog uses repository validation and has no dedicated delivery workflow. |
| Can be delivered independently | Yes | `tests/comitato/comitato_azure_retirements/test_platform_catalog.py` validates catalog-only changes. |
| Another area depends on it directionally | Yes | `src/comitato/comitato_azure_retirements/libs/runtime_runner.py` loads it during aggregation. |

Recorded count: 6.

### Azure Retirement Intelligence

| Signal | Verdict | Evidence |
| --- | --- | --- |
| Same word means different things inside and outside | Yes | Runtime scope selects subscriptions for collection, while governance scope binds policy assignments. |
| Represented differently from neighbouring areas | Yes | `src/comitato/comitato_azure_retirements/libs/`, `docs/comitato-azure-retirements-runtime.md` |
| Serves a different audience | Yes | `src/comitato/comitato_azure_retirements/README.md` defines committee review as the outcome. |
| Uses a different tool set | Yes | `.python-version`, `src/comitato/comitato_azure_retirements/requirements.txt` |
| Lives in a separate code base, state file, or schema | Yes | The runtime owns Python modules and ordered TSV schemas. |
| Follows a separate delivery process | Yes | `.github/workflows/_code-analysis.yml` and the focused pytest suite own its checks. |
| Can be delivered independently | Yes | `src/comitato/comitato_azure_retirements/run.sh` is a standalone CLI launcher. |
| Another area depends on it directionally | Yes | It consumes the platform catalog and Azure source APIs, then writes review artifacts. |

Recorded count: 8.

## Decision Drivers

* Keep policy-control, identity, catalog, and retirement-evidence language separate.
* Make independent state, schema, and execution boundaries easy to discover.
* Record the governance-to-identity and catalog-to-retirement dependencies without inventing other cross-domain links.

## Considered Options

* Keep one root `CONTEXT.md` for all repository terms.
* Use a root `CONTEXT-MAP.md` with only Azure Governance and Azure Retirement Intelligence contexts.
* Use a root `CONTEXT-MAP.md` with four evidence-backed contexts.
* Place context files beside the Terraform and Python source trees.

## Decision Outcome

Chosen option: "Use a root `CONTEXT-MAP.md` with four evidence-backed contexts", because each promoted area meets at least the required two signals and the map can express the evidenced governance-to-identity and catalog-to-retirement dependencies.

### Positive Consequences

* Readers can use the vocabulary for the area they are changing.
* The repository architecture can describe policy, identity, catalog, and retirement boundaries without merging them.
* Future changes can identify whether a new cross-domain dependency is architectural rather than accidental.

### Negative Consequences

* Contributors must select one of four contexts before changing domain vocabulary or rules.
* The context map and architecture must stay aligned as responsibilities move.
* Physical components may still share a domain even when they retain separate Terraform state.

## Pros and Cons of the Options

### Keep one root `CONTEXT.md`

* Good, because it is consistent with the current local declaration.
* Bad, because it merges terms, state, schemas, and lifecycles that are distinct in the repository.

### Use a root `CONTEXT-MAP.md` with two domain contexts

* Good, because it separates policy controls from retirement evidence.
* Bad, because it silently absorbs the independent Identity state and the catalog schema into unrelated contexts.

### Use a root `CONTEXT-MAP.md` with four domain contexts

* Good, because every promoted area meets the closed evidence threshold.
* Good, because it records both evidenced cross-domain dependencies without inventing an identity-to-workflow binding.
* Bad, because readers have more context documents to navigate.

### Place context files beside source trees

* Good, because each context is close to one implementation area.
* Bad, because the domain boundaries cross the physical source-tree boundaries and the topology rules prohibit treating a partial code directory as the domain home.
