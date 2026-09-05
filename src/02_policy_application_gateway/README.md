# Azure Policy: Application Gateway

This Terraform root defines the custom Azure Policy definitions for Application Gateway governance.

## Purpose

Use this directory for the Application Gateway policy family. The root loads policy parameters and rules from `policy_rules/`, resolves the `pagopa` management group, and exposes the policy IDs shown in the generated Terraform reference below. Start with `01_allowed_ciphersuites.tf`, `01_allowed_sku.tf`, and `01_required_zones.tf` when changing TLS, SKU, or availability-zone controls; use the local `terraform.sh` wrapper for the supported Terraform lifecycle actions.

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
| [azurerm_policy_definition.application_gateway_allowed_ciphersuites](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.application_gateway_allowed_sku](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.application_gateway_required_zones](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/management_group) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_application_gateway_allowed_ciphersuites_id"></a> [application\_gateway\_allowed\_ciphersuites\_id](#output\_application\_gateway\_allowed\_ciphersuites\_id) | n/a |
| <a name="output_application_gateway_allowed_sku_id"></a> [application\_gateway\_allowed\_sku\_id](#output\_application\_gateway\_allowed\_sku\_id) | n/a |
| <a name="output_application_gateway_required_zones_id"></a> [application\_gateway\_required\_zones\_id](#output\_application\_gateway\_required\_zones\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END_TF_DOCS -->
