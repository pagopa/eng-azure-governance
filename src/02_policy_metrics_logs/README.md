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
| [azurerm_policy_definition.metrics_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/management_group) | data source |
| [azurerm_role_definition.audit_logs_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/role_definition) | data source |
| [azurerm_role_definition.log_analytics_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/role_definition) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_metrics_logs_types"></a> [metrics\_logs\_types](#input\_metrics\_logs\_types) | Diagnostic Settings for metrics logs resource types | `list(string)` | <pre>[<br/>  "Microsoft.KeyVault/vaults",<br/>  "Microsoft.Network/virtualNetworkGateways",<br/>  "Microsoft.ContainerService/managedClusters",<br/>  "Microsoft.Network/publicIPAddresses",<br/>  "Microsoft.Network/networkInterfaces",<br/>  "Microsoft.EventHub/Namespace",<br/>  "Microsoft.Network/networkInterfaces",<br/>  "Microsoft.Network/virtualNetworks",<br/>  "Microsoft.Network/azureFirewalls",<br/>  "Microsoft.ContainerInstance/containerGroups",<br/>  "Microsoft.Compute/virtualMachineScaleSets",<br/>  "Microsoft.Network/loadBalancers"<br/>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
