# policy_assignments

<!-- markdownlint-disable -->
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.77.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_dev_assignments"></a> [dev\_assignments](#module\_dev\_assignments) | ./modules/dev | n/a |
| <a name="module_prod_assignments"></a> [prod\_assignments](#module\_prod\_assignments) | ./modules/prod | n/a |

## Resources

| Name | Type |
|------|------|
| [azurerm_management_group_policy_assignment.uat_api_management](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.uat_app_service](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.uat_log_analytics](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.uat_redis](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.uat_virtual_machine](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.uat_virtual_machine_scael_set](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_exemption.uat_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/management_group) | data source |
| [azurerm_management_group.uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/subscription) | data source |
| [azurerm_subscriptions.available](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/subscriptions) | data source |
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
