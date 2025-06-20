variable "audit_logs_workspace_id" {
  type        = string
  default     = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"
  description = "description"
}

variable "audit_logs_storage_westeurope" {
  type = object({
    id              = string
    name            = string
    resource_group  = string
    subscription_id = string
    retention_days  = string
    location        = string
  })
  default = {
    id              = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"
    name            = "ppseclogs"
    resource_group  = "sec-p-sentinel"
    subscription_id = "0da48c97-355f-4050-a520-f11a18b8be90"
    retention_days  = "365"
    location        = "westeurope"
  }
  description = "description"
}

variable "audit_logs_storage_northeurope" {
  type = object({
    id              = string
    name            = string
    resource_group  = string
    subscription_id = string
    retention_days  = string
    location        = string
  })
  default = {
    id              = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-rg-neu/providers/Microsoft.Storage/storageAccounts/ppseclogsneu"
    name            = "ppseclogsneu"
    resource_group  = "sec-p-rg-neu"
    subscription_id = "0da48c97-355f-4050-a520-f11a18b8be90"
    retention_days  = "365"
    location        = "northeurope"
  }
  description = "description"
}

variable "audit_logs_storage_italynorth" {
  type = object({
    id              = string
    name            = string
    resource_group  = string
    subscription_id = string
    retention_days  = string
    location        = string
  })
  default = {
    id              = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-rg-nit/providers/Microsoft.Storage/storageAccounts/ppseclogsitn"
    name            = "ppseclogsitn"
    resource_group  = "sec-p-rg-nit"
    subscription_id = "0da48c97-355f-4050-a520-f11a18b8be90"
    retention_days  = "365"
    location        = "italynorth"
  }
  description = "description"
}

resource "azurerm_policy_set_definition" "audit_logs" {
  name                = "audit_logs"
  policy_type         = "Custom"
  display_name        = "PagoPA Audit logs"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_prod"
    version  = "v1.0.0"
    ASC      = "true"
    parameterScopes = {
      for _, param in local.audit_logs : "${param.reference_id} : ${param.reference_id}" => data.azurerm_management_group.pagopa.id
    }
  })

  ## Key vault

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_log_analytics_id
    reference_id         = local.audit_logs.keyvault_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
    reference_id         = local.audit_logs.keyvault_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
    reference_id         = local.audit_logs.keyvault_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Application Gateway

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_log_analytics_id
    reference_id         = local.audit_logs.application_gateway_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_storage_account_id
    reference_id         = local.audit_logs.application_gateway_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_storage_account_id
    reference_id         = local.audit_logs.application_gateway_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Container Registry

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_log_analytics_id
    reference_id         = local.audit_logs.container_registry_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_storage_account_id
    reference_id         = local.audit_logs.container_registry_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_storage_account_id
    reference_id         = local.audit_logs.container_registry_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Kubernetes Cluster

  # policy_definition_reference {
  #   policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_log_analytics_id
  #   reference_id         = local.audit_logs.kubernetes_cluster_workspaceid.reference_id
  #   parameter_values = jsonencode({
  #     logAnalytics = {
  #       value = var.audit_logs_workspace_id
  #     }
  #   })
  # }
  #
  # policy_definition_reference {
  #   policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_storage_account_id
  #   reference_id         = local.audit_logs.kubernetes_cluster_storageid_westeurope.reference_id
  #   parameter_values = jsonencode({
  #     storageAccount = {
  #       value = var.audit_logs_storage_westeurope.id
  #     }
  #     location = {
  #       value = var.audit_logs_storage_westeurope.location
  #     }
  #   })
  # }
  #
  # policy_definition_reference {
  #   policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_storage_account_id
  #   reference_id         = local.audit_logs.kubernetes_cluster_storageid_northeurope.reference_id
  #   parameter_values = jsonencode({
  #     storageAccount = {
  #       value = var.audit_logs_storage_northeurope.id
  #     }
  #     location = {
  #       value = var.audit_logs_storage_northeurope.location
  #     }
  #   })
  # }

  ## Api Management

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_log_analytics_id
    reference_id         = local.audit_logs.api_management_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_storage_account_id
    reference_id         = local.audit_logs.api_management_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_storage_account_id
    reference_id         = local.audit_logs.api_management_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Postgresql Flexible

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_log_analytics_id
    reference_id         = local.audit_logs.postgresql_flexible_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_storage_account_id
    reference_id         = local.audit_logs.postgresql_flexible_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_storage_account_id
    reference_id         = local.audit_logs.postgresql_flexible_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Postgresql Flexible

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_log_analytics_id
    reference_id         = local.audit_logs.postgresql_single_server_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_storage_account_id
    reference_id         = local.audit_logs.postgresql_single_server_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_storage_account_id
    reference_id         = local.audit_logs.postgresql_single_server_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Log Analytics Workspace

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_log_analytics_id
    reference_id         = local.audit_logs.log_analytics_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_storage_account_id
    reference_id         = local.audit_logs.log_analytics_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_storage_account_id
    reference_id         = local.audit_logs.log_analytics_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Cosmos DB

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_log_analytics_id
    reference_id         = local.audit_logs.cosmos_db_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_storage_account_id
    reference_id         = local.audit_logs.cosmos_db_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_storage_account_id
    reference_id         = local.audit_logs.cosmos_db_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## App Service

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_log_analytics_id
    reference_id         = local.audit_logs.app_service_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_storage_account_id
    reference_id         = local.audit_logs.app_service_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_storage_account_id
    reference_id         = local.audit_logs.app_service_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Event Hub

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_log_analytics_id
    reference_id         = local.audit_logs.event_hub_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_storage_account_id
    reference_id         = local.audit_logs.event_hub_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_storage_account_id
    reference_id         = local.audit_logs.event_hub_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Public IP

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_log_analytics_id
    reference_id         = local.audit_logs.public_ip_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_storage_account_id
    reference_id         = local.audit_logs.public_ip_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_storage_account_id
    reference_id         = local.audit_logs.public_ip_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Virtual Network Gateway

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_log_analytics_id
    reference_id         = local.audit_logs.virtual_network_gateway_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_storage_account_id
    reference_id         = local.audit_logs.virtual_network_gateway_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_storage_account_id
    reference_id         = local.audit_logs.virtual_network_gateway_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Grafana

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_log_analytics_id
    reference_id         = local.audit_logs.grafana_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_storage_account_id
    reference_id         = local.audit_logs.grafana_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_storage_account_id
    reference_id         = local.audit_logs.grafana_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_northeurope.id
      }
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
    })
  }

  ## Subscription

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_subscription_log_analytics_id
    reference_id         = local.audit_logs.subscription_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_subscription_storage_account_id
    reference_id         = local.audit_logs.subscription_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_westeurope.id
      }
    })
  }

  # Azure SQL Server

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_azure_sql_server_log_analytics_id
    reference_id         = local.audit_logs.azure_sql_server_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_azure_sql_server_storage_account_id
    reference_id         = local.audit_logs.azure_sql_server_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
      retentionDays = {
        value = var.audit_logs_storage_westeurope.retention_days
      }
      storageAccountName = {
        value = var.audit_logs_storage_westeurope.name
      }
      storageAccountResourceGroup = {
        value = var.audit_logs_storage_westeurope.resource_group
      }
      storageAccountSubscriptionId = {
        value = var.audit_logs_storage_westeurope.subscription_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_azure_sql_server_storage_account_id
    reference_id         = local.audit_logs.azure_sql_server_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
      retentionDays = {
        value = var.audit_logs_storage_northeurope.retention_days
      }
      storageAccountName = {
        value = var.audit_logs_storage_northeurope.name
      }
      storageAccountResourceGroup = {
        value = var.audit_logs_storage_northeurope.resource_group
      }
      storageAccountSubscriptionId = {
        value = var.audit_logs_storage_northeurope.subscription_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_azure_sql_server_storage_account_id
    reference_id         = local.audit_logs.azure_sql_server_storageid_italynorth.reference_id
    parameter_values = jsonencode({
      location = {
        value = var.audit_logs_storage_italynorth.location
      }
      retentionDays = {
        value = var.audit_logs_storage_italynorth.retention_days
      }
      storageAccountName = {
        value = var.audit_logs_storage_italynorth.name
      }
      storageAccountResourceGroup = {
        value = var.audit_logs_storage_italynorth.resource_group
      }
      storageAccountSubscriptionId = {
        value = var.audit_logs_storage_italynorth.subscription_id
      }
    })
  }

  # Azure SQL Database

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_azure_sql_database_log_analytics_id
    reference_id         = local.audit_logs.azure_sql_database_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_azure_sql_database_storage_account_id
    reference_id         = local.audit_logs.azure_sql_database_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      location = {
        value = var.audit_logs_storage_westeurope.location
      }
      storageAccount = {
        value = var.audit_logs_storage_westeurope.name
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_azure_sql_database_storage_account_id
    reference_id         = local.audit_logs.azure_sql_database_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      location = {
        value = var.audit_logs_storage_northeurope.location
      }
      storageAccount = {
        value = var.audit_logs_storage_northeurope.name
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_azure_sql_database_storage_account_id
    reference_id         = local.audit_logs.azure_sql_database_storageid_italynorth.reference_id
    parameter_values = jsonencode({
      location = {
        value = var.audit_logs_storage_italynorth.location
      }
      storageAccount = {
        value = var.audit_logs_storage_italynorth.name
      }
    })
  }

}

output "audit_logs_id" {
  value = azurerm_policy_set_definition.audit_logs.id
}

output "audit_logs_workspace_id" {
  value = var.audit_logs_workspace_id
}

output "audit_logs_storage_id_westeurope" {
  value = var.audit_logs_storage_westeurope.id
}

output "audit_logs_storage_id_northeurope" {
  value = var.audit_logs_storage_northeurope.id
}

output "audit_logs_storage_id_italynorth" {
  value = var.audit_logs_storage_italynorth.id
}
