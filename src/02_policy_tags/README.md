# Azure Policy: Tags

This Terraform root defines custom Azure Policy controls for required tags and allowed tag values.

## Purpose

Use this directory for the tag policy definitions and their policy-rule parameter files. The root resolves the `pagopa` management group and exposes the policy IDs shown in the generated Terraform reference below.

## Validation

From this directory, run non-remote Terraform validation:

```bash
terraform fmt -check .
terraform init -backend=false -lockfile=readonly
terraform validate -no-color
```

No diagram is provided because this directory is a single policy root and the generated reference below enumerates its definitions, inputs, and outputs precisely.

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
| [azurerm_policy_definition.require_tag](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.require_tag_values](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/management_group) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
| <a name="output_tags_require_tag_id"></a> [tags\_require\_tag\_id](#output\_tags\_require\_tag\_id) | n/a |
| <a name="output_tags_require_tag_values_id"></a> [tags\_require\_tag\_values\_id](#output\_tags\_require\_tag\_values\_id) | n/a |
<!-- END_TF_DOCS -->
