# Azure Policy: Container Apps

This Terraform root defines custom Azure Policy definitions for Container Apps environments and jobs.

## Purpose

Use this directory for the Container Apps policy family. The policies require zone redundancy for managed environments and a zero minimum execution setting for matching GitHub self-hosted-runner jobs. Start with `01_enforce_multiaz.tf` or `01_min_execution.tf` and the matching files under `policy_rules/`; use the local `terraform.sh` wrapper for the supported Terraform lifecycle actions.

## Validation

From this directory, run non-remote Terraform validation:

```bash
terraform fmt -check .
terraform init -backend=false -lockfile=readonly
terraform validate -no-color
```

No diagram is provided because this directory is a single Terraform policy root and the generated reference below enumerates its definitions, inputs, and outputs more precisely than a separate relationship diagram.

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 4.35.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | 4.35.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_policy_definition.enforce_multiaz](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.min_execution](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
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
| <a name="output_enforce_multiaz_id"></a> [enforce\_multiaz\_id](#output\_enforce\_multiaz\_id) | n/a |
| <a name="output_min_execution_id"></a> [min\_execution\_id](#output\_min\_execution\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
