# azure-governance

This project contains all PagoPA policies and assignments to governance Azure workloads.

## Project structure

* `src/01_custom_roles` contains custom roles created with least privileges principle
* `src/02_policy_*` contains custom policies grouped by type definition
* `src/03_policy_set` contains custom policy initiatives (alias policy set)
* `src/04_policy_assignments` contains policy initiatives assignments to management groups or subscriptions.

## Policy overview

### audit_logs

`Type`: Compliance

`Scope`: Audit all resources that missing to send audit logs to security environment

`Assignment`: All production management groups or subscriptions

`Automatic remediation`: Yes

`Required roles by Managed Identity`:
- `Monitoring Contributor` on management groups or subscriptions
- `Log Analytics Contributor` on security Log Analitics Workspace and Storage Account

### resource_lock

`Type`: Compliance

`Scope`: Audit all resources that missing Resource Lock

`Assignment`: All production management groups or subscriptions

`Automatic remediation`: Yes

`Required roles by Managed Identity`:
- `PagoPA Resource Lock Contributor` on management groups or subscriptions

### data_sovereignty_eu

`Type`: Compliance

`Scope`: Deny to create resources outside EU regions. Allowed regions are: westeurope, northeurope, global

`Automatic remediation`: No

`Assignment`: Root PagoPA management group and child management groups or subscriptions

`Required roles by Managed Identity`: N/A

### tags_inherit_from_subscription

`Type`: Management

`Scope`: Assign standard tags to all resources inherited from subscription

`Automatic remediation`: Yes

`Assignment`: Root PagoPA management group and child management groups or subscriptions

`Required roles by Managed Identity`:
- `TODO` on management groups or subscriptions

## Terraform

Apply order is made by folders number.

### How to use it

```bash
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