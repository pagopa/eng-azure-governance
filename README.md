# eng-azure-governance

[![release](https://img.shields.io/github/v/release/pagopa/eng-azure-governance)](https://github.com/pagopa/eng-azure-governance/releases)
[![Static Analysis](https://github.com/pagopa/eng-azure-governance/actions/workflows/static_analysis.yml/badge.svg)](https://github.com/pagopa/eng-azure-governance/actions/workflows/static_analysis.yml)

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
az account set -s common

terraform init
terraform plan
terraform apply
```

## Azure policy docs

[Policy structure definition](https://docs.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure?WT.mc_id=Portal-Microsoft_Azure_Policy)

## How to force to rerun policy evaluation

```bash
# current subscription
az policy state trigger-scan --no-wait
# resource group in current subscription
az policy state trigger-scan -g "my-rg" --no-wait
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
