# policy

<!-- markdownlint-disable -->
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.77.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_policy_definition.app_service_allowed_linuxfxversion](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.app_service_allowed_sku](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.function_app_allowed_linuxfxversion](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_app_service_allowed_linuxfxversion_id"></a> [app\_service\_allowed\_linuxfxversion\_id](#output\_app\_service\_allowed\_linuxfxversion\_id) | n/a |
| <a name="output_app_service_allowed_sku_id"></a> [app\_service\_allowed\_sku\_id](#output\_app\_service\_allowed\_sku\_id) | n/a |
| <a name="output_function_app_allowed_linuxfxversion_id"></a> [function\_app\_allowed\_linuxfxversion\_id](#output\_function\_app\_allowed\_linuxfxversion\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END_TF_DOCS -->
