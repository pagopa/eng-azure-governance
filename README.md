# eng-azure-governance

[![release](https://img.shields.io/github/v/release/pagopa/eng-azure-governance)](https://github.com/pagopa/eng-azure-governance/releases)
[![Static Analysis](https://github.com/pagopa/eng-azure-governance/actions/workflows/static_analysis.yml/badge.svg)](https://github.com/pagopa/eng-azure-governance/actions/workflows/static_analysis.yml)
[![Terraform Drift Detection](https://github.com/pagopa/eng-azure-governance/actions/workflows/terraform_drift.yml/badge.svg)](https://github.com/pagopa/eng-azure-governance/actions/workflows/terraform_drift.yml)

This project contains all PagoPA policies and assignments to governance Azure workloads.

## Project structure

* `src/01_custom_roles` contains custom roles created with least privileges principle
* `src/02_policy_*` contains custom policies grouped by type definition
* `src/03_policy_set` contains custom policy initiatives (alias policy set)
* `src/04_policy_assignments` contains policy initiatives assignments to management groups or subscriptions.

## Terraform

Apply order is made by folders number.

### How to use it

```bash
./terraform.sh plan|apply|destroy
```

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
