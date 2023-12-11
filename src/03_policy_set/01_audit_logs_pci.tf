variable "audit_logs_pci_workspace_id" {
  type        = string
  default     = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"
  description = "description"
}

variable "audit_logs_pci_storage_primary_region" {
  type = object({
    storage_id = string,
    location   = string,
  })
  default = {
    storage_id = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"
    location   = "westeurope"
  }
  description = "description"
}

variable "audit_logs_pci_storage_secondary_region" {
  type = object({
    storage_id = string,
    location   = string,
  })
  default = {
    storage_id = "novalue"
    location   = "northeurope"
  }
  description = "description"
}

resource "azurerm_policy_set_definition" "audit_logs_pci" {
  name                = "audit_logs_pci"
  policy_type         = "Custom"
  display_name        = "PagoPA Audit logs PCI"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_pci"
    version  = "v1.0.0"
    ASC      = "true"
    parameterScopes = {
      for _, param in local.audit_logs : "${param.reference_id} : ${param.reference_id}" => data.azurerm_management_group.pagopa.id
    }
  })

  parameters = jsonencode({
    logAnalyticsId = {
      type = "String"
      metadata = {
        description = "Audit Logs workspace Id"
        displayName = "Audit Logs workspace Id"
      }
      defaultValue = var.audit_logs_pci_workspace_id
    }
    storageAccountPrimaryRegionId = {
      type = "String"
      metadata = {
        description = "Storage Account Id in Primary Region"
        displayName = "Storage Account Id in Primary Region"
      }
      defaultValue = var.audit_logs_pci_storage_primary_region.storage_id
    }
    storageAccountPrimaryRegionLocation = {
      type = "String"
      metadata = {
        description = "Storage Account Primary Region location"
        displayName = "Storage Account Primary Region location"
      }
      defaultValue = var.audit_logs_pci_storage_primary_region.location
    }
    storageAccountSecondaryRegionId = {
      type = "String"
      metadata = {
        description = "Storage Account Id in Secondary Region"
        displayName = "Storage Account Id in Secondary Region"
      }
      defaultValue = var.audit_logs_pci_storage_secondary_region.storage_id
    }
    storageAccountSecondaryRegionLocation = {
      type = "String"
      metadata = {
        description = "Storage Account Secondary Region location"
        displayName = "Storage Account Secondary Region location"
      }
      defaultValue = var.audit_logs_pci_storage_secondary_region.location
    }
  })

  ## Key vault

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_log_analytics_id
    reference_id         = local.audit_logs.keyvault_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
    reference_id         = local.audit_logs.keyvault_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
    reference_id         = local.audit_logs.keyvault_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }


  ## Application Gateway

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_log_analytics_id
    reference_id         = local.audit_logs.application_gateway_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_storage_account_id
    reference_id         = local.audit_logs.application_gateway_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_storage_account_id
    reference_id         = local.audit_logs.application_gateway_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Container Registry

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_log_analytics_id
    reference_id         = local.audit_logs.container_registry_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_storage_account_id
    reference_id         = local.audit_logs.container_registry_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_storage_account_id
    reference_id         = local.audit_logs.container_registry_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Kubernetes Cluster

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_log_analytics_id
    reference_id         = local.audit_logs.kubernetes_cluster_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_storage_account_id
    reference_id         = local.audit_logs.kubernetes_cluster_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_storage_account_id
    reference_id         = local.audit_logs.kubernetes_cluster_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Api Management

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_log_analytics_id
    reference_id         = local.audit_logs.api_management_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_storage_account_id
    reference_id         = local.audit_logs.api_management_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_storage_account_id
    reference_id         = local.audit_logs.api_management_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Postgresql Flexible

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_log_analytics_id
    reference_id         = local.audit_logs.postgresql_flexible_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_storage_account_id
    reference_id         = local.audit_logs.postgresql_flexible_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_storage_account_id
    reference_id         = local.audit_logs.postgresql_flexible_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Postgresql Flexible

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_log_analytics_id
    reference_id         = local.audit_logs.postgresql_single_server_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_storage_account_id
    reference_id         = local.audit_logs.postgresql_single_server_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_storage_account_id
    reference_id         = local.audit_logs.postgresql_single_server_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Log Analytics Workspace

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_log_analytics_id
    reference_id         = local.audit_logs.log_analytics_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_storage_account_id
    reference_id         = local.audit_logs.log_analytics_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_storage_account_id
    reference_id         = local.audit_logs.log_analytics_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Cosmos DB

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_log_analytics_id
    reference_id         = local.audit_logs.cosmos_db_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_storage_account_id
    reference_id         = local.audit_logs.cosmos_db_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_storage_account_id
    reference_id         = local.audit_logs.cosmos_db_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## App Service

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_log_analytics_id
    reference_id         = local.audit_logs.app_service_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_storage_account_id
    reference_id         = local.audit_logs.app_service_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_storage_account_id
    reference_id         = local.audit_logs.app_service_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Event Hub

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_log_analytics_id
    reference_id         = local.audit_logs.event_hub_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_storage_account_id
    reference_id         = local.audit_logs.event_hub_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_storage_account_id
    reference_id         = local.audit_logs.event_hub_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Public IP

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_log_analytics_id
    reference_id         = local.audit_logs.public_ip_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_storage_account_id
    reference_id         = local.audit_logs.public_ip_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_storage_account_id
    reference_id         = local.audit_logs.public_ip_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Virtual Network Gateway

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_log_analytics_id
    reference_id         = local.audit_logs.virtual_network_gateway_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_storage_account_id
    reference_id         = local.audit_logs.virtual_network_gateway_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_storage_account_id
    reference_id         = local.audit_logs.virtual_network_gateway_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

  ## Grafana

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_log_analytics_id
    reference_id         = local.audit_logs.grafana_workspaceid.reference_id
    parameter_values = jsonencode({
      logAnalytics = {
        value = "[parameters('logAnalyticsId')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_storage_account_id
    reference_id         = local.audit_logs.grafana_storageid_westeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountPrimaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_storage_account_id
    reference_id         = local.audit_logs.grafana_storageid_northeurope.reference_id
    parameter_values = jsonencode({
      storageAccount = {
        value = "[parameters('storageAccountSecondaryRegionId')]"
      }
      location = {
        value = "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    })
  }

}

output "audit_logs_pci_id" {
  value = azurerm_policy_set_definition.audit_logs_pci.id
}

output "audit_logs_pci_workspace_id" {
  value = var.audit_logs_pci_workspace_id
}

output "audit_logs_pci_storage_primary_region" {
  value = var.audit_logs_pci_storage_primary_region.storage_id
}

output "audit_logs_pci_storage_secondary_region" {
  value = var.audit_logs_pci_storage_secondary_region.storage_id
}
