<!-- markdownlint-disable -->
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.1.5 |
| <a name="requirement_azuread"></a> [azuread](#requirement\_azuread) | = 2.10.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 2.90.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_management_group_policy_assignment.dev_set_advice_2_root_sl_pay](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.dev_set_enforced_2_root_sl_pay](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.devops_set_advice_2_root_sl_pay](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.devops_set_enforced_2_root_sl_pay](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.prod_set_advice_2_root_sl_pay](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.prod_set_enforced_2_root_sl_pay](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.root_set_2_root_sl_pay](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.uat_set_advice_2_root_sl_pay](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.uat_set_enforced_2_root_sl_pay](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_policy_definition.tags_inherit_from_subscription](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_definition) | resource |
| [azurerm_policy_set_definition.dev_set_advice](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.dev_set_enforced](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.devops_set_advice](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.devops_set_enforced](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.prod_set_advice](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.prod_set_enforced](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.root_set](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.uat_set_advice](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.uat_set_enforced](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/resources/policy_set_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.dev_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.devops_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.prod_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.root_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.uat_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/2.90.0/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_dev_allowed_locations"></a> [dev\_allowed\_locations](#input\_dev\_allowed\_locations) | List of allowed locations for dev | `list(string)` | n/a | yes |
| <a name="input_dev_vm_skus_allowed"></a> [dev\_vm\_skus\_allowed](#input\_dev\_vm\_skus\_allowed) | list of skus allowed into management group dev | `list(string)` | n/a | yes |
| <a name="input_devops_allowed_locations"></a> [devops\_allowed\_locations](#input\_devops\_allowed\_locations) | List of allowed locations for devops | `list(string)` | n/a | yes |
| <a name="input_devops_vm_skus_allowed"></a> [devops\_vm\_skus\_allowed](#input\_devops\_vm\_skus\_allowed) | list of skus allowed into management group devops | `list(string)` | n/a | yes |
| <a name="input_location"></a> [location](#input\_location) | Location/Region name | `string` | n/a | yes |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | n/a | yes |
| <a name="input_prod_allowed_locations"></a> [prod\_allowed\_locations](#input\_prod\_allowed\_locations) | List of allowed locations for prod | `list(string)` | n/a | yes |
| <a name="input_prod_vm_skus_allowed"></a> [prod\_vm\_skus\_allowed](#input\_prod\_vm\_skus\_allowed) | list of skus allowed into management group prod | `list(string)` | n/a | yes |
| <a name="input_tags_subscription_to_inherith"></a> [tags\_subscription\_to\_inherith](#input\_tags\_subscription\_to\_inherith) | Tag that must be inherith by the subscription | `list(string)` | n/a | yes |
| <a name="input_uat_allowed_locations"></a> [uat\_allowed\_locations](#input\_uat\_allowed\_locations) | List of allowed locations for uat | `list(string)` | n/a | yes |
| <a name="input_uat_vm_skus_allowed"></a> [uat\_vm\_skus\_allowed](#input\_uat\_vm\_skus\_allowed) | list of skus allowed into management group uat | `list(string)` | n/a | yes |

## Outputs

No outputs.
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
