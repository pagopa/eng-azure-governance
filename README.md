# eng-azure-governance

[![release](https://img.shields.io/github/v/release/pagopa/eng-azure-governance)](https://github.com/pagopa/eng-azure-governance/releases)
[![Code Analysis](https://github.com/pagopa/eng-azure-governance/actions/workflows/_code-analysis.yml/badge.svg)](https://github.com/pagopa/eng-azure-governance/actions/workflows/_code-analysis.yml)
[![Terraform Drift Detection](https://github.com/pagopa/eng-azure-governance/actions/workflows/terraform_drift.yml/badge.svg)](https://github.com/pagopa/eng-azure-governance/actions/workflows/terraform_drift.yml)

This repository manages PagoPA Azure governance controls, its production workload identity, the Eng FinOps platform catalog, and Azure retirement evidence exports.

## Repository guide

- Use the [documentation index](docs/README.md) to find purpose, principles, standards, domain rules, and accepted decisions.
- Start with the [glossary map](GLOSSARY-MAP.md) for the repository vocabulary and domain boundaries.
- Read the [architecture](docs/architecture.md) for component responsibilities, flows, and validation paths.
- Read [Azure Governance](docs/domain/azure-governance/GLOSSARY.md) for policy vocabulary and [its rules](docs/domain/azure-governance/RULES.md).
- Read [Identity](docs/domain/identity/GLOSSARY.md) before changing the production workload identity or its grants.
- Read the [Eng FinOps Platform Catalog](docs/domain/eng-finops-platform-catalog/GLOSSARY.md) before changing the canonical subscription map and follow [its rules](docs/domain/eng-finops-platform-catalog/RULES.md).
- Read [Azure Retirement Intelligence](docs/domain/azure-retirements/GLOSSARY.md) for retirement-export vocabulary and [its rules](docs/domain/azure-retirements/RULES.md).

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
- [Graphify](#graphify)

## Project structure

- `.identity` owns the separately managed production identity, repository federation, Azure role grants, and Terraform state.
- `src/azure-policy/01_custom_roles` contains custom role definitions and is the first governance stage.
- `src/azure-policy/02_policy_*` contains policy families, each with its own Terraform root and state configuration.
- `src/azure-policy/03_policy_set` composes policy definitions into initiatives.
- `src/azure-policy/04_policy_assignments` assigns policy definitions and initiatives to management groups or subscriptions.
- `src/_source_of_truth` owns the canonical Eng FinOps platform catalog consumed by the retirement runtime.
- `src/comitato/comitato_azure_retirements_v2` publishes validated monthly retirement bundles, committee sidecars, and replayable acquisition evidence; see its [README](src/comitato/comitato_azure_retirements_v2/README.md).
- `src/scripts` contains the remediation and container-job operational scripts invoked by workflows.

## Terraform

Apply the numbered governance roots in `01` through `04` order. Each root owns a `terraform.sh` wrapper, but argument and backend layouts differ; run the local wrapper from its root.

### How to use it

```bash
cd src/azure-policy/01_custom_roles
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

Run the local code validator with the parallel execution and reporting engine
ported from AWS authorization v2 and the checks owned by this Azure repository:

```bash
./validate-code.sh
./validate-code.sh --list
./validate-code.sh --dry-run --compact
./validate-code.sh python --group retirements-v2
./validate-code.sh terraform --lane azure-policy
```

See [Code Validation](tools/validate_code/README.md) for prerequisites, selectors,
identity validation, parallelism, fail-fast, and JSON reports. These checks do not
invoke Terraform plan or apply. Provider initialization uses disabled remote
backends and read-only lockfiles. Existing failures are reported, not skipped.

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

- `src/azure-policy/01_custom_roles`: ruoli RBAC custom (JSON) per abilitare permessi minimi.
- `src/azure-policy/02_policy_*`: set di policy per dominio (es. networking, db, storage) con definizioni e parametri.
- `src/azure-policy/03_policy_set`: iniziative (PolicySet) che aggregano policy correlate con parametri predefiniti.
- `src/azure-policy/04_policy_assignments`: assignment verso Management Group con scope e parametri di iniziative/policy.
- eventuali `modules/`: moduli Terraform per deployment e riuso delle definizioni.

### Script

Gli script operativi sono in `src/scripts/`: `policy_remediation.sh` crea remediation e `update_container_app_job_graph.sh` gestisce i Container Apps Job. Il runtime Python per le evidenze di retirement è in `src/comitato/comitato_azure_retirements_v2/`; il relativo README descrive contratti e utilizzo.

### Workflow

- `terraform_drift.yml`: drift detection.
- `policy_remediation.yml`: remediation.
- `automation_scale_container_app_job.yml`: scaling automation.

### Note

Stato Terraform su storage `tfinforg` (container `terraform-state`, chiavi es. `eng-azure-governance.policy_<module>.terraform.tfstate`).

## Graphify

The repository knowledge graph is stored locally under the ignored `graphify-out/` directory.
Install Graphify from <https://github.com/safishamsi/graphify> and run:

```sh
make graphify-build
make graphify-hooks
make graphify-watch
```

`graphify-hooks` installs native `post-commit`, `post-checkout`, and `graph.json` merge hooks.
The watcher rebuilds code changes after a debounce; document and data changes create
`graphify-out/needs_update` and can be checked with `make graphify-check-update` before a
semantic `graphify extract .` run using the configured LLM backend.
