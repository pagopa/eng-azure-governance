# policy_assignments

<!-- markdownlint-disable -->
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.77.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_dev_assignments"></a> [dev\_assignments](#module\_dev\_assignments) | ./modules/dev | n/a |
| <a name="module_dev_pci_assignments"></a> [dev\_pci\_assignments](#module\_dev\_pci\_assignments) | ./modules/dev_pci | n/a |
| <a name="module_prod_assignments"></a> [prod\_assignments](#module\_prod\_assignments) | ./modules/prod | n/a |
| <a name="module_prod_pci_assignments"></a> [prod\_pci\_assignments](#module\_prod\_pci\_assignments) | ./modules/prod_pci | n/a |
| <a name="module_uat_assignments"></a> [uat\_assignments](#module\_uat\_assignments) | ./modules/uat | n/a |
| <a name="module_uat_pci_assignments"></a> [uat\_pci\_assignments](#module\_uat\_pci\_assignments) | ./modules/uat_pci | n/a |

## Resources

| Name | Type |
|------|------|
| [azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagopa_data_sovereignty_eu](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagopa_dns](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_assignment.pagopa_tags](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_assignment) | resource |
| [azurerm_management_group_policy_exemption.pagopa_azure_security_benchmark_mitigated](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_management_group_policy_exemption.pagopa_azure_security_benchmark_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/management_group_policy_exemption) | resource |
| [azurerm_resource_policy_exemption.pagopa_dns_pagopa_it_waiver](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/resource_policy_exemption) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/management_group) | data source |
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
<!-- END_TF_DOCS -->
