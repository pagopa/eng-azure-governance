# policy_set

<!-- markdownlint-disable -->
<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >=1.3.0 |
| <a name="requirement_azurerm"></a> [azurerm](#requirement\_azurerm) | = 3.77.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [azurerm_policy_set_definition.api_management_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.api_management_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.api_management_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.app_service_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.app_service_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.app_service_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.application_gateway_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.audit_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.audit_logs_pci](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.container_apps_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.cosmosdb_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.data_sovereignty_eu](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.dns](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.event_hub_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.key_vault_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.kubernetes_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.log_analytics_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.log_analytics_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.log_analytics_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.metrics_logs](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.networking_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.postgresql_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.postgresql_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.postgresql_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.redis_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.redis_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.redis_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.resource_lock](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.storage_account_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.tags](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.virtual_machine_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.virtual_machine_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.virtual_machine_scale_set_dev](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.virtual_machine_scale_set_prod](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.virtual_machine_scale_set_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_policy_set_definition.virtual_machine_uat](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/resources/policy_set_definition) | resource |
| [azurerm_client_config.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/client_config) | data source |
| [azurerm_management_group.pagopa](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/management_group) | data source |
| [azurerm_subscription.current](https://registry.terraform.io/providers/hashicorp/azurerm/3.77.0/docs/data-sources/subscription) | data source |
| [terraform_remote_state.policy_api_management](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_app_service](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_application_gateway](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_audit_logs](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_container_apps](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_cosmosdb](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_data_sovereignty](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_dns](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_event_hub](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_kubernetes](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_log_analytics](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_metrics_logs](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_networking](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_postgresql](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_redis](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_resource_lock](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_tags](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_virtual_machine](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |
| [terraform_remote_state.policy_virtual_machine_scale_set](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowed_locations"></a> [allowed\_locations](#input\_allowed\_locations) | List of allowed locations for resources | `list(string)` | <pre>[<br>  "italynorth",<br>  "northeurope",<br>  "westeurope",<br>  "global"<br>]</pre> | no |
| <a name="input_allowed_locations_resource_groups"></a> [allowed\_locations\_resource\_groups](#input\_allowed\_locations\_resource\_groups) | List of allowed locations for resource groups | `list(string)` | <pre>[<br>  "italynorth",<br>  "northeurope",<br>  "westeurope"<br>]</pre> | no |
| <a name="input_api_management_dev"></a> [api\_management\_dev](#input\_api\_management\_dev) | List of API Management policy set parameters | <pre>object({<br>    listofallowedskusname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskusname": [<br>    "Developer"<br>  ]<br>}</pre> | no |
| <a name="input_api_management_prod"></a> [api\_management\_prod](#input\_api\_management\_prod) | List of API Management policy set parameters | <pre>object({<br>    listofallowedskusname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskusname": [<br>    "Premium"<br>  ]<br>}</pre> | no |
| <a name="input_api_management_uat"></a> [api\_management\_uat](#input\_api\_management\_uat) | List of API Management policy set parameters | <pre>object({<br>    listofallowedskusname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskusname": [<br>    "Developer"<br>  ]<br>}</pre> | no |
| <a name="input_app_service_dev"></a> [app\_service\_dev](#input\_app\_service\_dev) | List of app service policy set parameters | <pre>object({<br>    listofallowedsku  = list(string)<br>    listofallowedkind = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedkind": [<br>    "elastic",<br>    "linux",<br>    "functionapp"<br>  ],<br>  "listofallowedsku": [<br>    "Y1",<br>    "WS1",<br>    "B1",<br>    "B2",<br>    "B3"<br>  ]<br>}</pre> | no |
| <a name="input_app_service_prod"></a> [app\_service\_prod](#input\_app\_service\_prod) | List of app service policy set parameters | <pre>object({<br>    listofallowedsku  = list(string)<br>    listofallowedkind = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedkind": [<br>    "elastic",<br>    "linux"<br>  ],<br>  "listofallowedsku": [<br>    "WS1",<br>    "P0v3",<br>    "P1v3"<br>  ]<br>}</pre> | no |
| <a name="input_app_service_uat"></a> [app\_service\_uat](#input\_app\_service\_uat) | List of app service policy set parameters | <pre>object({<br>    listofallowedsku  = list(string)<br>    listofallowedkind = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedkind": [<br>    "elastic",<br>    "linux",<br>    "functionapp"<br>  ],<br>  "listofallowedsku": [<br>    "Y1",<br>    "WS1",<br>    "B1",<br>    "B2",<br>    "B3"<br>  ]<br>}</pre> | no |
| <a name="input_audit_logs_pci_storage_ids"></a> [audit\_logs\_pci\_storage\_ids](#input\_audit\_logs\_pci\_storage\_ids) | n/a | `map(string)` | <pre>{<br>  "italynorth": "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogsitn",<br>  "northeurope": "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogsneu",<br>  "westeurope": "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"<br>}</pre> | no |
| <a name="input_audit_logs_pci_storage_regions"></a> [audit\_logs\_pci\_storage\_regions](#input\_audit\_logs\_pci\_storage\_regions) | n/a | `list(string)` | <pre>[<br>  "westeurope",<br>  "northeurope",<br>  "italynorth"<br>]</pre> | no |
| <a name="input_audit_logs_pci_workspace_id"></a> [audit\_logs\_pci\_workspace\_id](#input\_audit\_logs\_pci\_workspace\_id) | n/a | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"` | no |
| <a name="input_audit_logs_storage_ids"></a> [audit\_logs\_storage\_ids](#input\_audit\_logs\_storage\_ids) | n/a | `map(string)` | <pre>{<br>  "italynorth": "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogsitn",<br>  "northeurope": "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogsneu",<br>  "westeurope": "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"<br>}</pre> | no |
| <a name="input_audit_logs_storage_regions"></a> [audit\_logs\_storage\_regions](#input\_audit\_logs\_storage\_regions) | n/a | `list(string)` | <pre>[<br>  "westeurope",<br>  "northeurope",<br>  "italynorth"<br>]</pre> | no |
| <a name="input_audit_logs_workspace_id"></a> [audit\_logs\_workspace\_id](#input\_audit\_logs\_workspace\_id) | n/a | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"` | no |
| <a name="input_metrics_logs_pci_workspace_id"></a> [metrics\_logs\_pci\_workspace\_id](#input\_metrics\_logs\_pci\_workspace\_id) | description | `string` | `"/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"` | no |
| <a name="input_postgresql_dev"></a> [postgresql\_dev](#input\_postgresql\_dev) | List of PostgreSQL policy set parameters | <pre>object({<br>    listofallowedskuname         = list(string)<br>    listofallowedflexibleskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedflexibleskuname": [<br>    "Standard_B1ms",<br>    "Standard_B2s",<br>    "Standard_B2ms"<br>  ],<br>  "listofallowedskuname": [<br>    "B_Gen5_1",<br>    "B_Gen5_2",<br>    "GP_Gen5_2"<br>  ]<br>}</pre> | no |
| <a name="input_postgresql_prod"></a> [postgresql\_prod](#input\_postgresql\_prod) | List of PostgreSQL policy set parameters | <pre>object({<br>    listofallowedflexibleskuname = list(string)<br>    listofallowedskuname         = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedflexibleskuname": [<br>    "Standard_D2ds_v4",<br>    "Standard_D4ds_v4",<br>    "Standard_D8ds_v4",<br>    "Standard_D2ds_v5",<br>    "Standard_D4ds_v5",<br>    "Standard_D8ds_v5"<br>  ],<br>  "listofallowedskuname": [<br>    "GP_Gen5_2",<br>    "GP_Gen5_4",<br>    "GP_Gen5_8"<br>  ]<br>}</pre> | no |
| <a name="input_postgresql_uat"></a> [postgresql\_uat](#input\_postgresql\_uat) | List of PostgreSQL policy set parameters | <pre>object({<br>    listofallowedskuname         = list(string)<br>    listofallowedflexibleskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedflexibleskuname": [<br>    "Standard_B1ms",<br>    "Standard_B2s",<br>    "Standard_B2ms"<br>  ],<br>  "listofallowedskuname": [<br>    "GP_Gen5_2"<br>  ]<br>}</pre> | no |
| <a name="input_redis_dev"></a> [redis\_dev](#input\_redis\_dev) | List of redis policy set parameters | <pre>object({<br>    listofallowedskuname     = list(string)<br>    listofallowedskucapacity = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskucapacity": [<br>    "0",<br>    "1"<br>  ],<br>  "listofallowedskuname": [<br>    "Basic"<br>  ]<br>}</pre> | no |
| <a name="input_redis_prod"></a> [redis\_prod](#input\_redis\_prod) | List of redis policy set parameters | <pre>object({<br>    listofallowedskuname     = list(string)<br>    listofallowedskucapacity = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskucapacity": [<br>    "0",<br>    "1",<br>    "2"<br>  ],<br>  "listofallowedskuname": [<br>    "Standard",<br>    "Premium"<br>  ]<br>}</pre> | no |
| <a name="input_redis_uat"></a> [redis\_uat](#input\_redis\_uat) | List of redis policy set parameters | <pre>object({<br>    listofallowedskuname     = list(string)<br>    listofallowedskucapacity = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskucapacity": [<br>    "0",<br>    "1"<br>  ],<br>  "listofallowedskuname": [<br>    "Basic"<br>  ]<br>}</pre> | no |
| <a name="input_virtual_machine_dev"></a> [virtual\_machine\_dev](#input\_virtual\_machine\_dev) | List of Virtual Machine policy set parameters | <pre>object({<br>    listofallowedskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskuname": [<br>    "Standard_B2ms",<br>    "Standard_B4ms",<br>    "Standard_B8ms"<br>  ]<br>}</pre> | no |
| <a name="input_virtual_machine_prod"></a> [virtual\_machine\_prod](#input\_virtual\_machine\_prod) | List of Virtual Machine policy set parameters | <pre>object({<br>    listofallowedskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskuname": [<br>    "Standard_D2ds_v5",<br>    "Standard_D4ds_v5",<br>    "Standard_D8ds_v5"<br>  ]<br>}</pre> | no |
| <a name="input_virtual_machine_scale_set_dev"></a> [virtual\_machine\_scale\_set\_dev](#input\_virtual\_machine\_scale\_set\_dev) | List of Virtual Machine policy set parameters | <pre>object({<br>    listofallowedskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskuname": [<br>    "Standard_B2ms",<br>    "Standard_B4ms",<br>    "Standard_B8ms"<br>  ]<br>}</pre> | no |
| <a name="input_virtual_machine_scale_set_prod"></a> [virtual\_machine\_scale\_set\_prod](#input\_virtual\_machine\_scale\_set\_prod) | List of Virtual Machine policy set parameters | <pre>object({<br>    listofallowedskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskuname": [<br>    "Standard_B2ms",<br>    "Standard_B4ms",<br>    "Standard_B8ms"<br>  ]<br>}</pre> | no |
| <a name="input_virtual_machine_scale_set_uat"></a> [virtual\_machine\_scale\_set\_uat](#input\_virtual\_machine\_scale\_set\_uat) | List of Virtual Machine policy set parameters | <pre>object({<br>    listofallowedskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskuname": [<br>    "Standard_B2ms",<br>    "Standard_B4ms",<br>    "Standard_B8ms"<br>  ]<br>}</pre> | no |
| <a name="input_virtual_machine_uat"></a> [virtual\_machine\_uat](#input\_virtual\_machine\_uat) | List of Virtual Machine policy set parameters | <pre>object({<br>    listofallowedskuname = list(string)<br>  })</pre> | <pre>{<br>  "listofallowedskuname": [<br>    "Standard_B2ms",<br>    "Standard_B4ms",<br>    "Standard_B8ms"<br>  ]<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_api_management_dev_id"></a> [api\_management\_dev\_id](#output\_api\_management\_dev\_id) | n/a |
| <a name="output_api_management_prod_id"></a> [api\_management\_prod\_id](#output\_api\_management\_prod\_id) | n/a |
| <a name="output_api_management_uat_id"></a> [api\_management\_uat\_id](#output\_api\_management\_uat\_id) | n/a |
| <a name="output_app_service_dev_id"></a> [app\_service\_dev\_id](#output\_app\_service\_dev\_id) | n/a |
| <a name="output_app_service_prod_id"></a> [app\_service\_prod\_id](#output\_app\_service\_prod\_id) | n/a |
| <a name="output_app_service_uat_id"></a> [app\_service\_uat\_id](#output\_app\_service\_uat\_id) | n/a |
| <a name="output_application_gateway_prod_id"></a> [application\_gateway\_prod\_id](#output\_application\_gateway\_prod\_id) | n/a |
| <a name="output_audit_logs_id"></a> [audit\_logs\_id](#output\_audit\_logs\_id) | n/a |
| <a name="output_audit_logs_pci_id"></a> [audit\_logs\_pci\_id](#output\_audit\_logs\_pci\_id) | n/a |
| <a name="output_audit_logs_pci_storage_id_italynorth"></a> [audit\_logs\_pci\_storage\_id\_italynorth](#output\_audit\_logs\_pci\_storage\_id\_italynorth) | n/a |
| <a name="output_audit_logs_pci_storage_id_northeurope"></a> [audit\_logs\_pci\_storage\_id\_northeurope](#output\_audit\_logs\_pci\_storage\_id\_northeurope) | n/a |
| <a name="output_audit_logs_pci_storage_id_westeurope"></a> [audit\_logs\_pci\_storage\_id\_westeurope](#output\_audit\_logs\_pci\_storage\_id\_westeurope) | n/a |
| <a name="output_audit_logs_pci_workspace_id"></a> [audit\_logs\_pci\_workspace\_id](#output\_audit\_logs\_pci\_workspace\_id) | n/a |
| <a name="output_audit_logs_storage_id_italynorth"></a> [audit\_logs\_storage\_id\_italynorth](#output\_audit\_logs\_storage\_id\_italynorth) | n/a |
| <a name="output_audit_logs_storage_id_northeurope"></a> [audit\_logs\_storage\_id\_northeurope](#output\_audit\_logs\_storage\_id\_northeurope) | n/a |
| <a name="output_audit_logs_storage_id_westeurope"></a> [audit\_logs\_storage\_id\_westeurope](#output\_audit\_logs\_storage\_id\_westeurope) | n/a |
| <a name="output_audit_logs_workspace_id"></a> [audit\_logs\_workspace\_id](#output\_audit\_logs\_workspace\_id) | n/a |
| <a name="output_container_apps_prod_id"></a> [container\_apps\_prod\_id](#output\_container\_apps\_prod\_id) | n/a |
| <a name="output_cosmosdb_prod_id"></a> [cosmosdb\_prod\_id](#output\_cosmosdb\_prod\_id) | n/a |
| <a name="output_data_sovereignty_eu_id"></a> [data\_sovereignty\_eu\_id](#output\_data\_sovereignty\_eu\_id) | n/a |
| <a name="output_dns_id"></a> [dns\_id](#output\_dns\_id) | n/a |
| <a name="output_event_hub_prod_id"></a> [event\_hub\_prod\_id](#output\_event\_hub\_prod\_id) | n/a |
| <a name="output_key_vault_prod_id"></a> [key\_vault\_prod\_id](#output\_key\_vault\_prod\_id) | n/a |
| <a name="output_kubernetes_prod_id"></a> [kubernetes\_prod\_id](#output\_kubernetes\_prod\_id) | n/a |
| <a name="output_log_analytics_dev_id"></a> [log\_analytics\_dev\_id](#output\_log\_analytics\_dev\_id) | n/a |
| <a name="output_log_analytics_prod_id"></a> [log\_analytics\_prod\_id](#output\_log\_analytics\_prod\_id) | n/a |
| <a name="output_log_analytics_uat_id"></a> [log\_analytics\_uat\_id](#output\_log\_analytics\_uat\_id) | n/a |
| <a name="output_metrics_logs_id"></a> [metrics\_logs\_id](#output\_metrics\_logs\_id) | n/a |
| <a name="output_networking_prod_id"></a> [networking\_prod\_id](#output\_networking\_prod\_id) | n/a |
| <a name="output_postgresql_dev_id"></a> [postgresql\_dev\_id](#output\_postgresql\_dev\_id) | n/a |
| <a name="output_postgresql_prod_id"></a> [postgresql\_prod\_id](#output\_postgresql\_prod\_id) | n/a |
| <a name="output_postgresql_uat_id"></a> [postgresql\_uat\_id](#output\_postgresql\_uat\_id) | n/a |
| <a name="output_redis_dev_id"></a> [redis\_dev\_id](#output\_redis\_dev\_id) | n/a |
| <a name="output_redis_prod_id"></a> [redis\_prod\_id](#output\_redis\_prod\_id) | n/a |
| <a name="output_redis_uat_id"></a> [redis\_uat\_id](#output\_redis\_uat\_id) | n/a |
| <a name="output_resource_lock_id"></a> [resource\_lock\_id](#output\_resource\_lock\_id) | n/a |
| <a name="output_storage_account_prod_id"></a> [storage\_account\_prod\_id](#output\_storage\_account\_prod\_id) | n/a |
| <a name="output_tags_id"></a> [tags\_id](#output\_tags\_id) | n/a |
| <a name="output_virtual_machine_dev_id"></a> [virtual\_machine\_dev\_id](#output\_virtual\_machine\_dev\_id) | n/a |
| <a name="output_virtual_machine_prod_id"></a> [virtual\_machine\_prod\_id](#output\_virtual\_machine\_prod\_id) | n/a |
| <a name="output_virtual_machine_scale_set_dev_id"></a> [virtual\_machine\_scale\_set\_dev\_id](#output\_virtual\_machine\_scale\_set\_dev\_id) | n/a |
| <a name="output_virtual_machine_scale_set_prod_id"></a> [virtual\_machine\_scale\_set\_prod\_id](#output\_virtual\_machine\_scale\_set\_prod\_id) | n/a |
| <a name="output_virtual_machine_scale_set_uat_id"></a> [virtual\_machine\_scale\_set\_uat\_id](#output\_virtual\_machine\_scale\_set\_uat\_id) | n/a |
| <a name="output_virtual_machine_uat_id"></a> [virtual\_machine\_uat\_id](#output\_virtual\_machine\_uat\_id) | n/a |
<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->
