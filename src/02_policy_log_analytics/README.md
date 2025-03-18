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
| [azurerm_policy_definition.log_analytics_allowed_sku](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.log_analytics_bound_daily_quota](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.log_analytics_unbound_daily_quota](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_definition) | resource |
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
| <a name="output_log_analytics_allowed_sku_id"></a> [log\_analytics\_allowed\_sku\_id](#output\_log\_analytics\_allowed\_sku\_id) | n/a |
| <a name="output_log_analytics_bound_daily_quota_id"></a> [log\_analytics\_bound\_daily\_quota\_id](#output\_log\_analytics\_bound\_daily\_quota\_id) | n/a |
| <a name="output_log_analytics_unbound_daily_quota_id"></a> [log\_analytics\_unbound\_daily\_quota\_id](#output\_log\_analytics\_unbound\_daily\_quota\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END_TF_DOCS -->
