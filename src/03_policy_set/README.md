# policy_set

<!-- markdownlint-disable -->
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azuread"></a> [azuread](#requirement\_azuread) | = 2.31.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.38.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_policy_set_definition.application_gateway_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.audit_logs_pci](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.data_sovereignty_eu](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.storage_account_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/subscription) | data source |
| [terraform_remote_state.policy_application_gateway](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_audit_logs](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_resource_lock](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_tags_inherit_from_subscription](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowed_locations"></a> [allowed\_locations](#input\_allowed\_locations) | List of allowed locations for resources | `list(string)` | <pre>[<br>  "northeurope",<br>  "westeurope",<br>  "global"<br>]</pre> | no |
| <a name="input_allowed_locations_resource_groups"></a> [allowed\_locations\_resource\_groups](#input\_allowed\_locations\_resource\_groups) | List of allowed locations for resource groups | `list(string)` | <pre>[<br>  "northeurope",<br>  "westeurope"<br>]</pre> | no |
| <a name="input_audit_logs_pci_storage_primary_region"></a> [audit\_logs\_pci\_storage\_primary\_region](#input\_audit\_logs\_pci\_storage\_primary\_region) | description | <pre>object({<br>    storage_id = string,<br>    location   = string,<br>  })</pre> | <pre>{<br>  "location": "westeurope",<br>  "storage_id": "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"<br>}</pre> | no |
| <a name="input_audit_logs_pci_storage_secondary_region"></a> [audit\_logs\_pci\_storage\_secondary\_region](#input\_audit\_logs\_pci\_storage\_secondary\_region) | description | <pre>object({<br>    storage_id = string,<br>    location   = string,<br>  })</pre> | <pre>{<br>  "location": "northeurope",<br>  "storage_id": "novalue"<br>}</pre> | no |
| <a name="input_audit_logs_pci_workspace_id"></a> [audit\_logs\_pci\_workspace\_id](#input\_audit\_logs\_pci\_workspace\_id) | description | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"` | no |
| <a name="input_audit_logs_storage_id_northeurope"></a> [audit\_logs\_storage\_id\_northeurope](#input\_audit\_logs\_storage\_id\_northeurope) | description | `string` | `"novalue"` | no |
| <a name="input_audit_logs_storage_id_westeurope"></a> [audit\_logs\_storage\_id\_westeurope](#input\_audit\_logs\_storage\_id\_westeurope) | description | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"` | no |
| <a name="input_audit_logs_workspace_id"></a> [audit\_logs\_workspace\_id](#input\_audit\_logs\_workspace\_id) | description | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_application_gateway_prod_id"></a> [application\_gateway\_prod\_id](#output\_application\_gateway\_prod\_id) | n/a |
| <a name="output_audit_logs_id"></a> [audit\_logs\_id](#output\_audit\_logs\_id) | n/a |
| <a name="output_audit_logs_pci_id"></a> [audit\_logs\_pci\_id](#output\_audit\_logs\_pci\_id) | n/a |
| <a name="output_audit_logs_pci_storage_primary_region"></a> [audit\_logs\_pci\_storage\_primary\_region](#output\_audit\_logs\_pci\_storage\_primary\_region) | n/a |
| <a name="output_audit_logs_pci_storage_secondary_region"></a> [audit\_logs\_pci\_storage\_secondary\_region](#output\_audit\_logs\_pci\_storage\_secondary\_region) | n/a |
| <a name="output_audit_logs_pci_workspace_id"></a> [audit\_logs\_pci\_workspace\_id](#output\_audit\_logs\_pci\_workspace\_id) | n/a |
| <a name="output_audit_logs_storage_id_northeurope"></a> [audit\_logs\_storage\_id\_northeurope](#output\_audit\_logs\_storage\_id\_northeurope) | n/a |
| <a name="output_audit_logs_storage_id_westeurope"></a> [audit\_logs\_storage\_id\_westeurope](#output\_audit\_logs\_storage\_id\_westeurope) | n/a |
| <a name="output_audit_logs_workspace_id"></a> [audit\_logs\_workspace\_id](#output\_audit\_logs\_workspace\_id) | n/a |
| <a name="output_data_sovereignty_eu_id"></a> [data\_sovereignty\_eu\_id](#output\_data\_sovereignty\_eu\_id) | n/a |
| <a name="output_resource_lock_id"></a> [resource\_lock\_id](#output\_resource\_lock\_id) | n/a |
| <a name="output_storage_account_prod_id"></a> [storage\_account\_prod\_id](#output\_storage\_account\_prod\_id) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
