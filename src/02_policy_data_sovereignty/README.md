# Azure Policy: Data Sovereignty

This Terraform root defines custom Azure Policy definitions for allowed Azure locations.

## Purpose

Use this directory for the data-sovereignty policy family. One policy checks resource locations and one checks resource-group locations; both load their parameters and rules from `policy_rules/`, resolve the `pagopa` management group, and expose policy IDs through the Terraform outputs. Start with the matching `01_allowed_locations*.tf` and policy-rule files when changing the allowed-location contract.

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
| [azurerm_policy_definition.allowed_locations](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.allowed_locations_resource_group](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/management_group) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_allowed_locations_id"></a> [allowed\_locations\_id](#output\_allowed\_locations\_id) | n/a |
| <a name="output_allowed_locations_resource_group_id"></a> [allowed\_locations\_resource\_group\_id](#output\_allowed\_locations\_resource\_group\_id) | n/a |
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
<!-- END_TF_DOCS -->
