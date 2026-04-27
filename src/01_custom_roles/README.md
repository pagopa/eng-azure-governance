# custom_roles

This folder allows you to create a new role at the subscription level (you won't find it in azure ad > custom roles).

## PagoPA IaC Reader

This custom role allows the sp or users it is associated with to be able to launch terraform plans

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

| Name | Source | Version |
|------|--------|---------|
| <a name="module_dx_app_cd_resource_group_deploy"></a> [dx\_app\_cd\_resource\_group\_deploy](#module\_dx\_app\_cd\_resource\_group\_deploy) | git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles | implement-merge-roles-terraform-module |
| <a name="module_dx_app_ci_resource_group_reader"></a> [dx\_app\_ci\_resource\_group\_reader](#module\_dx\_app\_ci\_resource\_group\_reader) | git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles | implement-merge-roles-terraform-module |
| <a name="module_dx_infra_cd_private_networking"></a> [dx\_infra\_cd\_private\_networking](#module\_dx\_infra\_cd\_private\_networking) | git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles | implement-merge-roles-terraform-module |
| <a name="module_dx_infra_cd_resource_group_deploy"></a> [dx\_infra\_cd\_resource\_group\_deploy](#module\_dx\_infra\_cd\_resource\_group\_deploy) | git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles | implement-merge-roles-terraform-module |
| <a name="module_dx_infra_cd_subscription_admin"></a> [dx\_infra\_cd\_subscription\_admin](#module\_dx\_infra\_cd\_subscription\_admin) | git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles | implement-merge-roles-terraform-module |
| <a name="module_dx_infra_ci_resource_group_reader"></a> [dx\_infra\_ci\_resource\_group\_reader](#module\_dx\_infra\_ci\_resource\_group\_reader) | git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles | implement-merge-roles-terraform-module |
| <a name="module_dx_infra_ci_subscription_reader"></a> [dx\_infra\_ci\_subscription\_reader](#module\_dx\_infra\_ci\_subscription\_reader) | git::https://github.com/pagopa/dx.git//infra/modules/azure_merge_roles | implement-merge-roles-terraform-module |

## Resources

| Name | Type |
|------|------|
| [azurerm_role_definition.apim_list_secrets](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.apim_operator_app](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.applicationgateway_reader](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.audit_logs_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.authorization_reader](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.ddos_joiner](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.dns_takeover](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.dns_zone_reader](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.export_deployments_template](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.iac_reader](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.log_analytics_table_reader](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.opex_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.policy_exempt](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.policy_reader](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.policy_remediator](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.resource_lock_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.security_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.static_web_app_secrets](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.storage_blob_tags_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_role_definition.storage_queue_trigger](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/role_definition) | resource |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/data-sources/management_group) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_subscription_id"></a> [subscription\_id](#input\_subscription\_id) | The Azure subscription ID to use | `string` | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
