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
| [azurerm_policy_definition.kubernetes_allowed_kubernetes_version](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.kubernetes_allowed_sku](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.kubernetes_required_defender_profile](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.kubernetes_required_image_sha256](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.kubernetes_required_policy_addon](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
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
| <a name="output_kubernetes_allowed_kubernetes_version_id"></a> [kubernetes\_allowed\_kubernetes\_version\_id](#output\_kubernetes\_allowed\_kubernetes\_version\_id) | n/a |
| <a name="output_kubernetes_allowed_sku_id"></a> [kubernetes\_allowed\_sku\_id](#output\_kubernetes\_allowed\_sku\_id) | n/a |
| <a name="output_kubernetes_required_defender_profile_id"></a> [kubernetes\_required\_defender\_profile\_id](#output\_kubernetes\_required\_defender\_profile\_id) | n/a |
| <a name="output_kubernetes_required_image_sha256_id"></a> [kubernetes\_required\_image\_sha256\_id](#output\_kubernetes\_required\_image\_sha256\_id) | n/a |
| <a name="output_kubernetes_required_policy_addon_id"></a> [kubernetes\_required\_policy\_addon\_id](#output\_kubernetes\_required\_policy\_addon\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END_TF_DOCS -->
