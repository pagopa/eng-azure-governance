# policy_assignments

<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.1.0 |
| <a name="requirement_azuread"></a> [azuread](#requirement\_azuread) | = 2.29.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.28.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_management_group_policy_assignment.pagamenti_servizi_prod_resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagopa_data_sovereignty_eu](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_role_assignment.pagamenti_servizi_prod_resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/resources/role_assignment) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.dev_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.devops_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.landing_zones](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.platform_zones](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.prod_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.root_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.uat_sl_pagamenti_servizi](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.28.0/docs/data-sources/subscription) | data source |
| [terraform_remote_state.policy_set](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_location"></a> [location](#input\_location) | location | `string` | `"westeurope"` | no |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | `"Custom PagoPA"` | no |
| <a name="input_policy_type"></a> [policy\_type](#input\_policy\_type) | policy type | `string` | `"Custom"` | no |

## Outputs

No outputs.
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
