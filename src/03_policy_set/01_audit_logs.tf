variable "audit_logs_workspace_id" {
  type        = string
  default     = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"
  description = "description"
}

variable "audit_logs_storage_id_westeurope" {
  type        = string
  default     = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"
  description = "description"
}

variable "audit_logs_storage_id_northeurope" {
  type        = string
  default     = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogsneu"
  description = "description"
}

variable "audit_logs_storage_id_italynorth" {
  type        = string
  default     = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogsitn"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
    reference_id         = local.audit_logs.keyvault_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_storage_account_id
    reference_id         = local.audit_logs.application_gateway_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_storage_account_id
    reference_id         = local.audit_logs.container_registry_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
  #       value = var.audit_logs_storage_id_westeurope
  #     }
  #     location = {
  #       value = "westeurope"
  #     }
  #   })
  # }
  #
  # policy_definition_reference {
  #   policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_storage_account_id
  #   reference_id         = local.audit_logs.kubernetes_cluster_storageid_northeurope.reference_id
  #   parameter_values = jsonencode({
  #     storageAccount = {
  #       value = var.audit_logs_storage_id_northeurope
  #     }
  #     location = {
  #       value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_storage_account_id
    reference_id         = local.audit_logs.api_management_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_storage_account_id
    reference_id         = local.audit_logs.postgresql_flexible_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_storage_account_id
    reference_id         = local.audit_logs.postgresql_single_server_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_storage_account_id
    reference_id         = local.audit_logs.log_analytics_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_storage_account_id
    reference_id         = local.audit_logs.cosmos_db_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_storage_account_id
    reference_id         = local.audit_logs.app_service_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_storage_account_id
    reference_id         = local.audit_logs.event_hub_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_storage_account_id
    reference_id         = local.audit_logs.public_ip_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_storage_account_id
    reference_id         = local.audit_logs.virtual_network_gateway_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
      }
      location = {
        value = "westeurope"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_storage_account_id
    reference_id         = local.audit_logs.grafana_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_id_northeurope
      }
      location = {
        value = "northeurope"
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
        value = var.audit_logs_storage_id_westeurope
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
  value = var.audit_logs_storage_id_westeurope
}

output "audit_logs_storage_id_northeurope" {
  value = var.audit_logs_storage_id_northeurope
}
