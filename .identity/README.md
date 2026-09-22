# .identity

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.7.0 |
| <a name="requirement_azuread"></a> [azuread](#requirement\_azuread) | 2.47.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | 3.97.1 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_azurerm"></a> [azurerm](#provider\_azurerm) | 3.97.1 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_federated_identity_credential.prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/resources/federated_identity_credential) | resource |
| [azurerm_role_assignment.prod_container_app_job_contributor](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.prod_management_group_reader](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.prod_policy_reader](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.prod_policy_remediator](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/resources/role_assignment) | resource |
| [azurerm_role_assignment.prod_tfinforg](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/resources/role_assignment) | resource |
| [azurerm_user_assigned_identity.prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/resources/user_assigned_identity) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/data-sources/management_group) | data source |
| [azurerm_resource_group.identity](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/data-sources/resource_group) | data source |
| [azurerm_storage_account.tfinforg](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/data-sources/storage_account) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.97.1/docs/data-sources/subscription) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_env"></a> [env](#input\_env) | Environment | `string` | n/a | yes |
| <a name="input_env_short"></a> [env\_short](#input\_env\_short) | n/a | `string` | n/a | yes |
| <a name="input_github"></a> [github](#input\_github) | GitHub Organization and repository name | <pre>object({<br/>    org        = string<br/>    repository = string<br/>  })</pre> | n/a | yes |
| <a name="input_prefix"></a> [prefix](#input\_prefix) | n/a | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_azure_main"></a> [azure\_main](#output\_azure\_main) | n/a |
| <a name="output_subscription_id"></a> [subscription\_id](#output\_subscription\_id) | n/a |
| <a name="output_tenant_id"></a> [tenant\_id](#output\_tenant\_id) | n/a |
<!-- END_TF_DOCS -->
