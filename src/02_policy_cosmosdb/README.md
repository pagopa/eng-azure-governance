# policy

<!-- markdownlint-disable -->
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azuread"></a> [azuread](#requirement\_azuread) | = 2.31.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.38.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_policy_definition.cosmosdb_allowed_tls](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_forbidden_capabilities_policy](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_required_backup_policy](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_required_network](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_cosmosdb_allowed_tls_id"></a> [cosmosdb\_allowed\_tls\_id](#output\_cosmosdb\_allowed\_tls\_id) | n/a |
| <a name="output_cosmosdb_forbidden_capabilities_id"></a> [cosmosdb\_forbidden\_capabilities\_id](#output\_cosmosdb\_forbidden\_capabilities\_id) | n/a |
| <a name="output_cosmosdb_required_backup_policy_id"></a> [cosmosdb\_required\_backup\_policy\_id](#output\_cosmosdb\_required\_backup\_policy\_id) | n/a |
| <a name="output_cosmosdb_required_network_id"></a> [cosmosdb\_required\_network\_id](#output\_cosmosdb\_required\_network\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
