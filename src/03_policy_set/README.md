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
| [azurerm_policy_set_definition.app_service_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.app_service_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.app_service_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.application_gateway_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.audit_logs_pci](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.cosmosdb_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.data_sovereignty_eu](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.dns](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.event_hub_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.kubernetes_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.log_analytics_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.metrics_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.networking_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.redis_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.redis_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.redis_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.storage_account_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.virtual_machine_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.virtual_machine_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/resources/policy_set_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.38.0/docs/data-sources/subscription) | data source |
| [terraform_remote_state.policy_app_service](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_application_gateway](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_audit_logs](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_cosmosdb](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_data_sovereignty](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_dns](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_event_hub](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_kubernetes](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_metrics_logs](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_redis](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_resource_lock](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_tags_inherit_from_subscription](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_virtual_machine](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowed_locations"></a> [allowed\_locations](#input\_allowed\_locations) | List of allowed locations for resources | `list(string)` | <pre>[<br>  "italynorth",<br>  "northeurope",<br>  "westeurope",<br>  "global"<br>]</pre> | no |
| <a name="input_allowed_locations_resource_groups"></a> [allowed\_locations\_resource\_groups](#input\_allowed\_locations\_resource\_groups) | List of allowed locations for resource groups | `list(string)` | <pre>[<br>  "italynorth",<br>  "northeurope",<br>  "westeurope"<br>]</pre> | no |
| <a name="input_app_service_dev"></a> [app\_service\_dev](#input\_app\_service\_dev) | List of app service policy set parameters | <pre>object({<br>    listofallowedsku  = list(string)<br>    listofallowedkind = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedkind": [<br>    "elastic",<br>    "linux",<br>    "functionapp"<br>  ],<br>  "listofallowedsku": [<br>    "Y1",<br>    "WS1",<br>    "B1",<br>    "B2",<br>    "B3"<br>  ]<br>}</pre> | no |
| <a name="input_app_service_prod"></a> [app\_service\_prod](#input\_app\_service\_prod) | List of app service policy set parameters | <pre>object({<br>    listofallowedsku  = list(string)<br>    listofallowedkind = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedkind": [<br>    "elastic",<br>    "linux"<br>  ],<br>  "listofallowedsku": [<br>    "WS1",<br>    "P0v3",<br>    "P1v3"<br>  ]<br>}</pre> | no |
| <a name="input_app_service_uat"></a> [app\_service\_uat](#input\_app\_service\_uat) | List of app service policy set parameters | <pre>object({<br>    listofallowedsku  = list(string)<br>    listofallowedkind = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedkind": [<br>    "elastic",<br>    "linux",<br>    "functionapp"<br>  ],<br>  "listofallowedsku": [<br>    "Y1",<br>    "WS1",<br>    "B1",<br>    "B2",<br>    "B3"<br>  ]<br>}</pre> | no |
| <a name="input_audit_logs_pci_storage_primary_region"></a> [audit\_logs\_pci\_storage\_primary\_region](#input\_audit\_logs\_pci\_storage\_primary\_region) | description | <pre>object({<br>    storage_id = string,<br>    location   = string,<br>  })</pre> | <pre>{<br>  "location": "westeurope",<br>  "storage_id": "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"<br>}</pre> | no |
| <a name="input_audit_logs_pci_storage_secondary_region"></a> [audit\_logs\_pci\_storage\_secondary\_region](#input\_audit\_logs\_pci\_storage\_secondary\_region) | description | <pre>object({<br>    storage_id = string,<br>    location   = string,<br>  })</pre> | <pre>{<br>  "location": "northeurope",<br>  "storage_id": "novalue"<br>}</pre> | no |
| <a name="input_audit_logs_pci_workspace_id"></a> [audit\_logs\_pci\_workspace\_id](#input\_audit\_logs\_pci\_workspace\_id) | description | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"` | no |
| <a name="input_audit_logs_storage_id_northeurope"></a> [audit\_logs\_storage\_id\_northeurope](#input\_audit\_logs\_storage\_id\_northeurope) | description | `string` | `"novalue"` | no |
| <a name="input_audit_logs_storage_id_westeurope"></a> [audit\_logs\_storage\_id\_westeurope](#input\_audit\_logs\_storage\_id\_westeurope) | description | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"` | no |
| <a name="input_audit_logs_workspace_id"></a> [audit\_logs\_workspace\_id](#input\_audit\_logs\_workspace\_id) | description | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"` | no |
| <a name="input_metrics_logs_pci_workspace_id"></a> [metrics\_logs\_pci\_workspace\_id](#input\_metrics\_logs\_pci\_workspace\_id) | description | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"` | no |
| <a name="input_networking_prod"></a> [networking\_prod](#input\_networking\_prod) | List of app service policy set parameters | <pre>object({<br>    ddosplanid = string<br>  })</pre> | <pre>{<br>  "ddosplanid": "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-ddos/providers/Microsoft.Network/ddosProtectionPlans/sec-p-ddos-protection"<br>}</pre> | no |
| <a name="input_redis_dev"></a> [redis\_dev](#input\_redis\_dev) | List of redis policy set parameters | <pre>object({<br>    listofallowedskuname     = list(string)<br>    listofallowedskucapacity = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskucapacity": [<br>    "0",<br>    "1"<br>  ],<br>  "listofallowedskuname": [<br>    "Basic"<br>  ]<br>}</pre> | no |
| <a name="input_redis_prod"></a> [redis\_prod](#input\_redis\_prod) | List of redis policy set parameters | <pre>object({<br>    listofallowedskuname     = list(string)<br>    listofallowedskucapacity = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskucapacity": [<br>    "0",<br>    "1",<br>    "2"<br>  ],<br>  "listofallowedskuname": [<br>    "Standard",<br>    "Premium"<br>  ]<br>}</pre> | no |
| <a name="input_redis_uat"></a> [redis\_uat](#input\_redis\_uat) | List of redis policy set parameters | <pre>object({<br>    listofallowedskuname     = list(string)<br>    listofallowedskucapacity = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskucapacity": [<br>    "0",<br>    "1"<br>  ],<br>  "listofallowedskuname": [<br>    "Basic"<br>  ]<br>}</pre> | no |
| <a name="input_virtual_machine_dev"></a> [virtual\_machine\_dev](#input\_virtual\_machine\_dev) | List of Virtual Machine policy set parameters | <pre>object({<br>    listofallowedskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskuname": [<br>    "Standard_B2ms",<br>    "Standard_B4ms",<br>    "Standard_B8ms"<br>  ]<br>}</pre> | no |
| <a name="input_virtual_machine_prod"></a> [virtual\_machine\_prod](#input\_virtual\_machine\_prod) | List of Virtual Machine policy set parameters | <pre>object({<br>    listofallowedskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskuname": [<br>    "Standard_D2ds_v5",<br>    "Standard_D4ds_v5",<br>    "Standard_D8ds_v5"<br>  ]<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_app_service_dev_id"></a> [app\_service\_dev\_id](#output\_app\_service\_dev\_id) | n/a |
| <a name="output_app_service_prod_id"></a> [app\_service\_prod\_id](#output\_app\_service\_prod\_id) | n/a |
| <a name="output_app_service_uat_id"></a> [app\_service\_uat\_id](#output\_app\_service\_uat\_id) | n/a |
| <a name="output_application_gateway_prod_id"></a> [application\_gateway\_prod\_id](#output\_application\_gateway\_prod\_id) | n/a |
| <a name="output_audit_logs_id"></a> [audit\_logs\_id](#output\_audit\_logs\_id) | n/a |
| <a name="output_audit_logs_pci_id"></a> [audit\_logs\_pci\_id](#output\_audit\_logs\_pci\_id) | n/a |
| <a name="output_audit_logs_pci_storage_primary_region"></a> [audit\_logs\_pci\_storage\_primary\_region](#output\_audit\_logs\_pci\_storage\_primary\_region) | n/a |
| <a name="output_audit_logs_pci_storage_secondary_region"></a> [audit\_logs\_pci\_storage\_secondary\_region](#output\_audit\_logs\_pci\_storage\_secondary\_region) | n/a |
| <a name="output_audit_logs_pci_workspace_id"></a> [audit\_logs\_pci\_workspace\_id](#output\_audit\_logs\_pci\_workspace\_id) | n/a |
| <a name="output_audit_logs_storage_id_northeurope"></a> [audit\_logs\_storage\_id\_northeurope](#output\_audit\_logs\_storage\_id\_northeurope) | n/a |
| <a name="output_audit_logs_storage_id_westeurope"></a> [audit\_logs\_storage\_id\_westeurope](#output\_audit\_logs\_storage\_id\_westeurope) | n/a |
| <a name="output_audit_logs_workspace_id"></a> [audit\_logs\_workspace\_id](#output\_audit\_logs\_workspace\_id) | n/a |
| <a name="output_cosmosdb_prod_id"></a> [cosmosdb\_prod\_id](#output\_cosmosdb\_prod\_id) | n/a |
| <a name="output_data_sovereignty_eu_id"></a> [data\_sovereignty\_eu\_id](#output\_data\_sovereignty\_eu\_id) | n/a |
| <a name="output_dns_id"></a> [dns\_id](#output\_dns\_id) | n/a |
| <a name="output_event_hub_prod_id"></a> [event\_hub\_prod\_id](#output\_event\_hub\_prod\_id) | n/a |
| <a name="output_kubernetes_prod_id"></a> [kubernetes\_prod\_id](#output\_kubernetes\_prod\_id) | n/a |
| <a name="output_log_analytics_dev_id"></a> [log\_analytics\_dev\_id](#output\_log\_analytics\_dev\_id) | n/a |
| <a name="output_metrics_logs_id"></a> [metrics\_logs\_id](#output\_metrics\_logs\_id) | n/a |
| <a name="output_networking_prod_id"></a> [networking\_prod\_id](#output\_networking\_prod\_id) | n/a |
| <a name="output_redis_dev_id"></a> [redis\_dev\_id](#output\_redis\_dev\_id) | n/a |
| <a name="output_redis_prod_id"></a> [redis\_prod\_id](#output\_redis\_prod\_id) | n/a |
| <a name="output_redis_uat_id"></a> [redis\_uat\_id](#output\_redis\_uat\_id) | n/a |
| <a name="output_resource_lock_id"></a> [resource\_lock\_id](#output\_resource\_lock\_id) | n/a |
| <a name="output_storage_account_prod_id"></a> [storage\_account\_prod\_id](#output\_storage\_account\_prod\_id) | n/a |
| <a name="output_virtual_machine_dev_id"></a> [virtual\_machine\_dev\_id](#output\_virtual\_machine\_dev\_id) | n/a |
| <a name="output_virtual_machine_prod_id"></a> [virtual\_machine\_prod\_id](#output\_virtual\_machine\_prod\_id) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
