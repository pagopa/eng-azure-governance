# policy

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.1.0 |
| <a name="requirement_azuread"></a> [azuread](#requirement\_azuread) | = 2.29.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.28.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_policy_definition.audit_logs_application_gateway_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_application_gateway_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_keyvault_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.audit_logs_keyvault_storage_account](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/resources/policy_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_audit_logs_application_gateway_log_analytics_id"></a> [audit\_logs\_application\_gateway\_log\_analytics\_id](#output\_audit\_logs\_application\_gateway\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_application_gateway_storage_account_id"></a> [audit\_logs\_application\_gateway\_storage\_account\_id](#output\_audit\_logs\_application\_gateway\_storage\_account\_id) | n/a |
| <a name="output_audit_logs_keyvault_log_analytics_id"></a> [audit\_logs\_keyvault\_log\_analytics\_id](#output\_audit\_logs\_keyvault\_log\_analytics\_id) | n/a |
| <a name="output_audit_logs_keyvault_storage_account_id"></a> [audit\_logs\_keyvault\_storage\_account\_id](#output\_audit\_logs\_keyvault\_storage\_account\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->