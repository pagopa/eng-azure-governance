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
| [azurerm_policy_definition.resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.tags_inherit_from_subscription](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/resources/policy_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.root_pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_policy_type"></a> [policy\_type](#input\_policy\_type) | policy type | `string` | `"Custom"` | no |
| <a name="input_resource_lock"></a> [resource\_lock](#input\_resource\_lock) | Resource lock types | `list(string)` | <pre>[<br>  "Microsoft.DocumentDB/databaseAccounts",<br>  "Microsoft.Storage/storageAccounts",<br>  "Microsoft.Cache/Redis",<br>  "Microsoft.Network/publicIPAddresses",<br>  "Microsoft.DBforPostgreSQL/servers",<br>  "Microsoft.DBforPostgreSQL/flexibleServers",<br>  "Microsoft.DataProtection/backupVaults",<br>  "Microsoft.Network/applicationGateways",<br>  "Microsoft.OperationalInsights/workspaces"<br>]</pre> | no |
| <a name="input_resource_lock_role_id"></a> [resource\_lock\_role\_id](#input\_resource\_lock\_role\_id) | Resource lock role for managed identity https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles | `string` | `"18d7d88d-d35e-4fb5-a5c3-7773c20a72d9"` | no |
| <a name="input_tags_inherit_from_subscription"></a> [tags\_inherit\_from\_subscription](#input\_tags\_inherit\_from\_subscription) | Tag that must be inherith from the subscription | `list(string)` | <pre>[<br>  "CostCenter",<br>  "Environment",<br>  "Owner",<br>  "BusinessUnit"<br>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_resource_lock_ids"></a> [resource\_lock\_ids](#output\_resource\_lock\_ids) | n/a |
| <a name="output_tags_inherit_from_subscription_ids"></a> [tags\_inherit\_from\_subscription\_ids](#output\_tags\_inherit\_from\_subscription\_ids) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
