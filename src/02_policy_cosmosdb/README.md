# Azure Policy: Cosmos DB

This Terraform root defines the custom Azure Policy definitions for Cosmos DB governance.

## Purpose

Use this directory for the Cosmos DB policy family. The root loads policy parameters and rules from `policy_rules/`, resolves the `pagopa` management group, and exposes the policy IDs shown in the generated Terraform reference below. The controls cover capacity mode, TLS, failover, scaling, backup, network restrictions, and zone redundancy; start with the matching `01_*.tf` and policy-rule files when changing one of those controls.

## Validation

From this directory, run non-remote Terraform validation:

```bash
terraform fmt -check .
terraform init -backend=false -lockfile=readonly
terraform validate -no-color
```

No diagram is provided because this directory is a single Terraform policy root and the generated reference below enumerates its definitions, inputs, and outputs more precisely than a separate relationship diagram.

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
| [azurerm_policy_definition.cosmosdb_allowed_capacity_mode](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_allowed_tls](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_automatic_failover_enabled](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_dynamic_scaling_enabled](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_forbidden_secondary_zone_redundancy](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_required_backup_policy](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_required_network](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.cosmosdb_required_primary_zone_redundancy](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/management_group) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_cosmosdb_allowed_capacity_mode_id"></a> [cosmosdb\_allowed\_capacity\_mode\_id](#output\_cosmosdb\_allowed\_capacity\_mode\_id) | n/a |
| <a name="output_cosmosdb_allowed_tls_id"></a> [cosmosdb\_allowed\_tls\_id](#output\_cosmosdb\_allowed\_tls\_id) | n/a |
| <a name="output_cosmosdb_automatic_failover_enabled_id"></a> [cosmosdb\_automatic\_failover\_enabled\_id](#output\_cosmosdb\_automatic\_failover\_enabled\_id) | n/a |
| <a name="output_cosmosdb_dynamic_scaling_enabled_id"></a> [cosmosdb\_dynamic\_scaling\_enabled\_id](#output\_cosmosdb\_dynamic\_scaling\_enabled\_id) | n/a |
| <a name="output_cosmosdb_forbidden_secondary_zone_redundancy_id"></a> [cosmosdb\_forbidden\_secondary\_zone\_redundancy\_id](#output\_cosmosdb\_forbidden\_secondary\_zone\_redundancy\_id) | n/a |
| <a name="output_cosmosdb_required_backup_policy_id"></a> [cosmosdb\_required\_backup\_policy\_id](#output\_cosmosdb\_required\_backup\_policy\_id) | n/a |
| <a name="output_cosmosdb_required_network_id"></a> [cosmosdb\_required\_network\_id](#output\_cosmosdb\_required\_network\_id) | n/a |
| <a name="output_cosmosdb_required_primary_zone_redundancy_id"></a> [cosmosdb\_required\_primary\_zone\_redundancy\_id](#output\_cosmosdb\_required\_primary\_zone\_redundancy\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END_TF_DOCS -->
