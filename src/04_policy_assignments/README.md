# policy_assignments

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
| <a name="provider_terraform"></a> [terraform](#provider\_terraform) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_dev_assignments"></a> [dev\_assignments](#module\_dev\_assignments) | ./modules/dev | n/a |
| <a name="module_prod_assignments"></a> [prod\_assignments](#module\_prod\_assignments) | ./modules/prod | n/a |
| <a name="module_uat_assignments"></a> [uat\_assignments](#module\_uat\_assignments) | ./modules/uat | n/a |

## Resources

| Name | Type |
|------|------|
| [azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagopa_data_sovereignty_eu](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagopa_dns](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_exemption.pagopa_azure_security_benchmark_mitigated](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagopa_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_resource_policy_exemption.pagopa_dns_pagopa_it_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_policy_exemption) | resource |
| [azurerm_resource_policy_exemption.pictresourcelock_ip_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_policy_exemption) | resource |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/management_group) | data source |
| [azurerm_subscriptions.available](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/subscriptions) | data source |
| [terraform_remote_state.policy_set](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_location"></a> [location](#input\_location) | location | `string` | n/a | yes |
| <a name="input_metadata_category_name"></a> [metadata\_category\_name](#input\_metadata\_category\_name) | metadata category name | `string` | n/a | yes |
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |
| <a name="input_subscriptions_by_env"></a> [subscriptions\_by\_env](#input\_subscriptions\_by\_env) | Subscription display names grouped by environment | <pre>object({<br/>    dev  = list(string)<br/>    uat  = list(string)<br/>    prod = list(string)<br/>  })</pre> | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
