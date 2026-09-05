# eng-azure-governance

[![release](https://img.shields.io/github/v/release/pagopa/eng-azure-governance)](https://github.com/pagopa/eng-azure-governance/releases)
[![Code Analysis](https://github.com/pagopa/eng-azure-governance/actions/workflows/_code-analysis.yml/badge.svg)](https://github.com/pagopa/eng-azure-governance/actions/workflows/_code-analysis.yml)
[![Terraform Drift Detection](https://github.com/pagopa/eng-azure-governance/actions/workflows/terraform_drift.yml/badge.svg)](https://github.com/pagopa/eng-azure-governance/actions/workflows/terraform_drift.yml)

This repository manages PagoPA Azure governance controls, its production workload identity, the Eng FinOps platform catalog, and Azure retirement evidence exports.

## Repository guide

- Start with the [context map](CONTEXT-MAP.md) for the repository vocabulary and domain boundaries.
- Read the [architecture](docs/architecture.md) for component responsibilities, flows, and validation paths.
- Read [Azure Governance](docs/domain/azure-governance/CONTEXT.md) for policy vocabulary and [its rules](docs/domain/azure-governance/RULES.md).
- Read [Identity](docs/domain/identity/CONTEXT.md) before changing the production workload identity or its grants.
- Read the [Eng FinOps Platform Catalog](docs/domain/eng-finops-platform-catalog/CONTEXT.md) before changing the canonical subscription map and follow [its rules](docs/domain/eng-finops-platform-catalog/RULES.md).
- Read [Azure Retirement Intelligence](docs/domain/azure-retirements/CONTEXT.md) for retirement-export vocabulary and [its rules](docs/domain/azure-retirements/RULES.md).

No diagram is provided here because the repository-wide policy and workflow relationships are maintained in [docs/architecture.md](docs/architecture.md).

## Contents

- [Repository guide](#repository-guide)
- [Project structure](#project-structure)
- [Terraform](#terraform)
- [Validation](#validation)
- [Azure policy docs](#azure-policy-docs)
- [How to force to rerun policy evaluation](#how-to-force-to-rerun-policy-evaluation)
- [Terraform lock.hcl](#terraform-lockhcl)
- [Repository Structure & Details (Auto-generated)](#repository-structure--details-auto-generated)

## Project structure

- `.identity` owns the separately managed production identity, repository federation, Azure role grants, and Terraform state.
- `src/01_custom_roles` contains custom role definitions and is the first governance stage.
- `src/02_policy_*` contains policy families, each with its own Terraform root and state configuration.
- `src/03_policy_set` composes policy definitions into initiatives.
- `src/04_policy_assignments` assigns policy definitions and initiatives to management groups or subscriptions.
- `src/_source_of_truth` owns the canonical Eng FinOps platform catalog consumed by the retirement runtime.
- `src/comitato/comitato_azure_retirements` collects and projects retirement evidence for committee review.
- `src/scripts` contains the remediation and container-job operational scripts invoked by workflows.

## Terraform

Apply the numbered governance roots in `01` through `04` order. Each root owns a `terraform.sh` wrapper, but argument and backend layouts differ; run the local wrapper from its root.

### How to use it

```bash
cd src/01_custom_roles
./terraform.sh plan
```

### Identity root

The hidden `.identity` root is outside the numbered policy sequence. It provisions the production user-assigned identity, its GitHub environment federation, and bounded Azure role assignments in a dedicated Terraform state.

```bash
cd .identity
./terraform.sh plan prod
```

Its outputs expose tenant, subscription, and identity metadata. Checked-in files do not prove which outputs populate the `AZ_*` GitHub environment secrets, so do not infer that binding from matching names.

## Validation

Use non-mutating checks before review:

```bash
terraform fmt -check -recursive .identity
terraform fmt -check -recursive src
make test
```

The repository pre-commit configuration adds Terraform validation with remote backends disabled, ShellCheck, actionlint, Python checks, and structured-data checks.

## Azure policy docs

[Policy structure definition](https://docs.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure?WT.mc_id=Portal-Microsoft_Azure_Policy)

## How to force to rerun policy evaluation

```bash
# change subscription
az account set -s MY-SUBSCRIPTION
# trigger scan on current subscription
az policy state trigger-scan --no-wait
# trigger scan on resource group in current subscription
az policy state trigger-scan -g my-rg --no-wait
```

## Terraform lock.hcl

We have both developers who work with your Terraform configuration on their Linux, macOS or Windows workstations and automated systems that apply the configuration while running on Linux.
<https://www.terraform.io/docs/cli/commands/providers/lock.html#specifying-target-platforms>

So we need to specify this in terraform lock providers:

```sh
terraform init

rm .terraform.lock.hcl

terraform providers lock \
  -platform=windows_amd64 \
  -platform=darwin_amd64 \
  -platform=darwin_arm64 \
  -platform=linux_amd64
```

---
## Repository Structure & Details (Auto-generated)

### Scopo
Repository centrale per le Azure Policy d’organizzazione; definisce ruoli RBAC custom, policy singole e initiative e le assegna ai Management Group per imporre controlli di sicurezza/compliance su subscription e workload. Garantisce applicazione coerente dei guardrail e remediation automatica su larga scala.

### Cartelle
- `src/01_custom_roles`: ruoli RBAC custom (JSON) per abilitare permessi minimi.
- `src/02_policy_*`: set di policy per dominio (es. networking, db, storage) con definizioni e parametri.
- `src/03_policy_set`: iniziative (PolicySet) che aggregano policy correlate con parametri predefiniti.
- `src/04_policy_assignments`: assignment verso Management Group con scope e parametri di iniziative/policy.
- eventuali `modules/`: moduli Terraform per deployment e riuso delle definizioni.

### Script
Nessuno; tutto è definizione Policy/Initiative/Assignment.

### Workflow
- `terraform_drift.yml`: drift detection.
- `policy_remediation.yml`: remediation.
- `automation_scale_container_app_job.yml`: scaling automation.

### Note
Stato Terraform su storage `tfinforg` (container `terraform-state`, chiavi es. `eng-azure-governance.policy_<module>.terraform.tfstate`).
