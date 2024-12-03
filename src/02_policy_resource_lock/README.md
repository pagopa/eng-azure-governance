# policy

<!-- markdownlint-disable -->
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
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
| [azurerm_policy_definition.resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/management_group) | data source |
| [azurerm_role_definition.resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/role_definition) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_resource_lock_types"></a> [resource\_lock\_types](#input\_resource\_lock\_types) | Resource lock types | `list(string)` | <pre>[<br/>  "Microsoft.DocumentDB/databaseAccounts",<br/>  "Microsoft.Storage/storageAccounts",<br/>  "Microsoft.Cache/Redis",<br/>  "Microsoft.Network/publicIPAddresses",<br/>  "Microsoft.DBforPostgreSQL/servers",<br/>  "Microsoft.DBforPostgreSQL/flexibleServers",<br/>  "Microsoft.DataProtection/backupVaults",<br/>  "Microsoft.Network/applicationGateways",<br/>  "Microsoft.Network/natGateways",<br/>  "Microsoft.Network/virtualNetworkGateways",<br/>  "Microsoft.OperationalInsights/workspaces",<br/>  "microsoft.insights/components",<br/>  "Microsoft.ContainerService/ManagedClusters",<br/>  "Microsoft.Cdn/profiles",<br/>  "Microsoft.KeyVault/vaults",<br/>  "Microsoft.EventHub/Namespaces",<br/>  "Microsoft.EventHub/namespaces/eventhubs",<br/>  "Microsoft.DataFactory/factories",<br/>  "Microsoft.Kusto/Clusters",<br/>  "Microsoft.ManagedIdentity/userAssignedIdentities",<br/>  "Microsoft.NotificationHubs/namespaces",<br/>  "Microsoft.NotificationHubs/namespaces/notificationHubs"<br/>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
