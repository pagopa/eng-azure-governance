# policy

<!-- markdownlint-disable -->
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 4.35.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_policy_definition.eventhub_allowed_tls](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.eventhub_required_network](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.eventhub_required_zone_redundant](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_eventhub_allowed_tls_id"></a> [eventhub\_allowed\_tls\_id](#output\_eventhub\_allowed\_tls\_id) | n/a |
| <a name="output_eventhub_required_network_id"></a> [eventhub\_required\_network\_id](#output\_eventhub\_required\_network\_id) | n/a |
| <a name="output_eventhub_required_zone_redundant_id"></a> [eventhub\_required\_zone\_redundant\_id](#output\_eventhub\_required\_zone\_redundant\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END_TF_DOCS -->
