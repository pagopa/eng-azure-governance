# dev_pci

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 4.35.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_role_assignment.audit_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.audit_logs_contributor_storage_westeurope](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.audit_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.metrics_logs_contributor_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.metrics_logs_monitoring_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/role_assignment) | resource |
| [azurerm_subscription_policy_assignment.audit_logs_pci](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.metrics_logs](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/subscription_policy_assignment) | resource |
| [azurerm_subscription_policy_assignment.pcidssv4](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/subscription_policy_assignment) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_audit_logs"></a> [audit\_logs](#input\_audit\_logs) | Audit logs configuration | `map(string)` | <pre>{<br/>  "storage_primary_region_location": "novalue",<br/>  "storage_primary_region_storage_id": "novalue",<br/>  "storage_secondary_region_location": "novalue",<br/>  "storage_secondary_region_storage_id": "novalue",<br/>  "workspace_id": "novalue"<br/>}</pre> | no |
| <a name="input_location"></a> [location](#input\_location) | The Azure Region where the Policy Assignment should exist | `string` | n/a | yes |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | Metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_metrics_logs"></a> [metrics\_logs](#input\_metrics\_logs) | Metrics logs configuration | `map(string)` | <pre>{<br/>  "workspace_id": "novalue"<br/>}</pre> | no |
| <a name="input_policy_set_ids"></a> [policy\_set\_ids](#input\_policy\_set\_ids) | A map for each policy set id to assign | `map(string)` | n/a | yes |
| <a name="input_subscription"></a> [subscription](#input\_subscription) | The Subsription where this Policy Assignment should be created | <pre>object({<br/>    id              = string<br/>    subscription_id = string<br/>    display_name    = string<br/>  })</pre> | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
