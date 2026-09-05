# Azure Policy: Resource Locks

This Terraform root defines the custom Azure Policy control that requires resource locks for governed resource types.

## Purpose

Use this directory for the resource-lock policy and its configurable resource-type list. The root resolves the resource-lock contributor role and the `pagopa` management group, then exposes the policy ID shown in the generated Terraform reference below.

## Validation

From this directory, run non-remote Terraform validation:

```bash
terraform fmt -check .
terraform init -backend=false -lockfile=readonly
terraform validate -no-color
```

No diagram is provided because this directory is a single policy root and the generated reference below enumerates its definition, inputs, and output precisely.

<!-- markdownlint-disable -->
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
| [azurerm_policy_definition.resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/management_group) | data source |
| [azurerm_role_definition.resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/role_definition) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_resource_lock_types"></a> [resource\_lock\_types](#input\_resource\_lock\_types) | Resource lock types | `list(string)` | <pre>[<br/>  "Microsoft.DocumentDB/databaseAccounts",<br/>  "Microsoft.Storage/storageAccounts",<br/>  "Microsoft.Cache/Redis",<br/>  "Microsoft.Network/publicIPAddresses",<br/>  "Microsoft.DBforPostgreSQL/servers",<br/>  "Microsoft.DBforPostgreSQL/flexibleServers",<br/>  "Microsoft.DataProtection/backupVaults",<br/>  "Microsoft.Network/applicationGateways",<br/>  "Microsoft.Network/natGateways",<br/>  "Microsoft.Network/virtualNetworkGateways",<br/>  "Microsoft.OperationalInsights/workspaces",<br/>  "microsoft.insights/components",<br/>  "Microsoft.ContainerService/ManagedClusters",<br/>  "Microsoft.Cdn/profiles",<br/>  "Microsoft.KeyVault/vaults",<br/>  "Microsoft.EventHub/Namespaces",<br/>  "Microsoft.EventHub/namespaces/eventhubs",<br/>  "Microsoft.DataFactory/factories",<br/>  "Microsoft.Kusto/Clusters",<br/>  "Microsoft.ManagedIdentity/userAssignedIdentities",<br/>  "Microsoft.NotificationHubs/namespaces",<br/>  "Microsoft.NotificationHubs/namespaces/notificationHubs"<br/>]</pre> | no |
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END_TF_DOCS -->
