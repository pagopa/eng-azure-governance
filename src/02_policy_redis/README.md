# Azure Policy: Redis

This Terraform root defines custom Azure Policy controls for Azure Cache for Redis.

## Purpose

Use this directory for allowed Redis SKUs, TLS versions, and engine versions, disabling the non-SSL port, and requiring zone redundancy. The root resolves the current subscription, client configuration, and `pagopa` management group, then exposes the policy IDs in the generated Terraform reference below.

## Validation

From this directory, run non-remote Terraform validation:

```bash
terraform fmt -check .
terraform init -backend=false -lockfile=readonly
terraform validate -no-color
```

No diagram is provided because this directory is a single policy root and the generated reference below enumerates its definitions, inputs, and outputs precisely.

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
| [azurerm_policy_definition.redis_allowed_sku](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.redis_allowed_tls](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.redis_allowed_versions](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.redis_disable_nosslport](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.redis_required_zone_redundant](https://registry.terraform.io/providers/hashicorp/azurerm/4.35.0/docs/resources/policy_definition) | resource |
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
| <a name="output_policy_ids"></a> [policy\_ids](#output\_policy\_ids) | n/a |
| <a name="output_redis_allowed_sku_id"></a> [redis\_allowed\_sku\_id](#output\_redis\_allowed\_sku\_id) | n/a |
| <a name="output_redis_allowed_tls_id"></a> [redis\_allowed\_tls\_id](#output\_redis\_allowed\_tls\_id) | n/a |
| <a name="output_redis_allowed_versions_id"></a> [redis\_allowed\_versions\_id](#output\_redis\_allowed\_versions\_id) | n/a |
| <a name="output_redis_disable_nosslport_id"></a> [redis\_disable\_nosslport\_id](#output\_redis\_disable\_nosslport\_id) | n/a |
| <a name="output_redis_required_zone_redundant_id"></a> [redis\_required\_zone\_redundant\_id](#output\_redis\_required\_zone\_redundant\_id) | n/a |

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
| [azurerm_policy_definition.redis_allowed_sku](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.redis_allowed_tls](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.redis_allowed_versions](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.redis_disable_nosslport](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
| [azurerm_policy_definition.redis_required_zone_redundant](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/policy_definition) | resource |
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
| <a name="output_redis_allowed_sku_id"></a> [redis\_allowed\_sku\_id](#output\_redis\_allowed\_sku\_id) | n/a |
| <a name="output_redis_allowed_tls_id"></a> [redis\_allowed\_tls\_id](#output\_redis\_allowed\_tls\_id) | n/a |
| <a name="output_redis_allowed_versions_id"></a> [redis\_allowed\_versions\_id](#output\_redis\_allowed\_versions\_id) | n/a |
| <a name="output_redis_disable_nosslport_id"></a> [redis\_disable\_nosslport\_id](#output\_redis\_disable\_nosslport\_id) | n/a |
| <a name="output_redis_required_zone_redundant_id"></a> [redis\_required\_zone\_redundant\_id](#output\_redis\_required\_zone\_redundant\_id) | n/a |
<!-- END_TF_DOCS -->