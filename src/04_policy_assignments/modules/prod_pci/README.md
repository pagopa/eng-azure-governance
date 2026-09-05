# Azure Policy Assignments: Production PCI DSS

This Terraform module assigns the production PCI DSS policy controls to an Azure subscription.

## Purpose

Use this module for PCI DSS audit-log, metrics-log, PCI DSS v4, and storage-account policy assignments, including the supporting monitoring, Log Analytics, and storage role assignments. The generated Terraform reference below lists the module's inputs and assignments.

## Validation

From this directory, run non-remote Terraform validation:

```bash
terraform fmt -check .
terraform init -backend=false -lockfile=readonly
terraform validate -no-color
```

No diagram is provided because this module is a single subscription-assignment boundary and the generated Terraform reference below enumerates its inputs and resources precisely.

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | ~> 4.63.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | 4.63.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_role_assignment.audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.metrics_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.metrics_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_assignment) | resource |
| [azurerm_subscription_policy_assignment.audit_logs_pci](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.metrics_logs](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.pcidssv4](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subscription_policy_assignment) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_location"></a> [location](#input\_location) | The Azure Region where the Policy Assignment should exist | `string` | n/a | yes |
| <a name="input_policy_set_ids"></a> [policy\_set\_ids](#input\_policy\_set\_ids) | A map for each policy set id to assign | `map(string)` | n/a | yes |
| <a name="input_subscription"></a> [subscription](#input\_subscription) | The Subsription where this Policy Assignment should be created | <pre>object({<br/>    id              = string<br/>    subscription_id = string<br/>    display_name    = string<br/>  })</pre> | n/a | yes |
| <a name="input_audit_logs"></a> [audit\_logs](#input\_audit\_logs) | Audit logs configuration | `map(string)` | <pre>{<br/>  "storage_primary_region_location": "novalue",<br/>  "storage_primary_region_storage_id": "novalue",<br/>  "storage_secondary_region_location": "novalue",<br/>  "storage_secondary_region_storage_id": "novalue",<br/>  "workspace_id": "novalue"<br/>}</pre> | no |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | Metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_metrics_logs"></a> [metrics\_logs](#input\_metrics\_logs) | Metrics logs configuration | `map(string)` | <pre>{<br/>  "workspace_id": "novalue"<br/>}</pre> | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
