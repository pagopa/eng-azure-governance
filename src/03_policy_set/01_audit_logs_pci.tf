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

  metadata = <<METADATA
    {
        "category": "pagopa_pci",
        "version": "v1.0.0",
        "ASC": "true",
        "parameterScopes": {
          "${local.audit_logs.keyvault_workspaceid_reference_id} : ${local.audit_logs.keyvault_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.keyvault_storageid_westeurope_reference_id} : ${local.audit_logs.keyvault_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.keyvault_storageid_northeurope_reference_id} : ${local.audit_logs.keyvault_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.application_gateway_workspaceid_reference_id} : ${local.audit_logs.application_gateway_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.application_gateway_storageid_westeurope_reference_id} : ${local.audit_logs.application_gateway_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.application_gateway_storageid_northeurope_reference_id} : ${local.audit_logs.application_gateway_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.container_registry_workspaceid_reference_id} : ${local.audit_logs.container_registry_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.container_registry_storageid_westeurope_reference_id} : ${local.audit_logs.container_registry_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.container_registry_storageid_northeurope_reference_id} : ${local.audit_logs.container_registry_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.kubernetes_cluster_workspaceid_reference_id} : ${local.audit_logs.kubernetes_cluster_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.kubernetes_cluster_storageid_westeurope_reference_id} : ${local.audit_logs.kubernetes_cluster_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.kubernetes_cluster_storageid_northeurope_reference_id} : ${local.audit_logs.kubernetes_cluster_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.api_management_workspaceid_reference_id} : ${local.audit_logs.api_management_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.api_management_storageid_westeurope_reference_id} : ${local.audit_logs.api_management_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.api_management_storageid_northeurope_reference_id} : ${local.audit_logs.api_management_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.postgresql_flexible_workspaceid_reference_id} : ${local.audit_logs.postgresql_flexible_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.postgresql_flexible_storageid_westeurope_reference_id} : ${local.audit_logs.postgresql_flexible_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.postgresql_flexible_storageid_northeurope_reference_id} : ${local.audit_logs.postgresql_flexible_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.postgresql_single_server_workspaceid_reference_id} : ${local.audit_logs.postgresql_single_server_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.postgresql_single_server_storageid_westeurope_reference_id} : ${local.audit_logs.postgresql_single_server_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.postgresql_single_server_storageid_northeurope_reference_id} : ${local.audit_logs.postgresql_single_server_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.log_analytics_workspaceid_reference_id} : ${local.audit_logs.log_analytics_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.log_analytics_storageid_westeurope_reference_id} : ${local.audit_logs.log_analytics_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.log_analytics_storageid_northeurope_reference_id} : ${local.audit_logs.log_analytics_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.cosmos_db_workspaceid_reference_id} : ${local.audit_logs.cosmos_db_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.cosmos_db_storageid_westeurope_reference_id} : ${local.audit_logs.cosmos_db_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.cosmos_db_storageid_northeurope_reference_id} : ${local.audit_logs.cosmos_db_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.app_service_workspaceid_reference_id} : ${local.audit_logs.app_service_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.app_service_storageid_westeurope_reference_id} : ${local.audit_logs.app_service_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.app_service_storageid_northeurope_reference_id} : ${local.audit_logs.app_service_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.event_hub_workspaceid_reference_id} : ${local.audit_logs.event_hub_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.event_hub_storageid_westeurope_reference_id} : ${local.audit_logs.event_hub_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.event_hub_storageid_northeurope_reference_id} : ${local.audit_logs.event_hub_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.public_ip_workspaceid_reference_id} : ${local.audit_logs.public_ip_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.public_ip_storageid_westeurope_reference_id} : ${local.audit_logs.public_ip_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.public_ip_storageid_northeurope_reference_id} : ${local.audit_logs.public_ip_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.virtual_network_gateway_workspaceid_reference_id} : ${local.audit_logs.virtual_network_gateway_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.virtual_network_gateway_storageid_westeurope_reference_id} : ${local.audit_logs.virtual_network_gateway_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.virtual_network_gateway_storageid_northeurope_reference_id} : ${local.audit_logs.virtual_network_gateway_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.grafana_workspaceid_reference_id} : ${local.audit_logs.grafana_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.grafana_storageid_westeurope_reference_id} : ${local.audit_logs.grafana_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.grafana_storageid_northeurope_reference_id} : ${local.audit_logs.grafana_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}"
        }
    }
METADATA

  parameters = <<PARAMETERS
    {
        "logAnalyticsId": {
            "type": "String",
            "metadata": {
                "description": "Audit Logs workspace Id",
                "displayName": "Audit Logs workspace Id"
            },
            "defaultValue": "${var.audit_logs_pci_workspace_id}"
        },
        "storageAccountPrimaryRegionId": {
            "type": "String",
            "metadata": {
                "description": "Storage Account Id in Primary Region",
                "displayName": "Storage Account Id in Primary Region"
            },
            "defaultValue": "${var.audit_logs_pci_storage_primary_region.storage_id}"
        },
        "storageAccountPrimaryRegionLocation": {
            "type": "String",
            "metadata": {
                "description": "Storage Account Primary Region location",
                "displayName": "Storage Account Primary Region location"
            },
            "defaultValue": "${var.audit_logs_pci_storage_primary_region.location}"
        },
        "storageAccountSecondaryRegionId": {
            "type": "String",
            "metadata": {
                "description": "Storage Account Id in Secondary Region",
                "displayName": "Storage Account Id in Secondary Region"
            },
            "defaultValue": "${var.audit_logs_pci_storage_secondary_region.storage_id}"
        },
        "storageAccountSecondaryRegionLocation": {
            "type": "String",
            "metadata": {
                "description": "Storage Account Secondary Region location",
                "displayName": "Storage Account Secondary Region location"
            },
            "defaultValue": "${var.audit_logs_pci_storage_secondary_region.location}"
        }
    }
PARAMETERS

  ## Key vault

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_log_analytics_id
    reference_id         = local.audit_logs.keyvault_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
    reference_id         = local.audit_logs.keyvault_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
    reference_id         = local.audit_logs.keyvault_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }


  ## Application Gateway

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_log_analytics_id
    reference_id         = local.audit_logs.application_gateway_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_storage_account_id
    reference_id         = local.audit_logs.application_gateway_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_storage_account_id
    reference_id         = local.audit_logs.application_gateway_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Container Registry

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_log_analytics_id
    reference_id         = local.audit_logs.container_registry_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_storage_account_id
    reference_id         = local.audit_logs.container_registry_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_storage_account_id
    reference_id         = local.audit_logs.container_registry_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Kubernetes Cluster

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_log_analytics_id
    reference_id         = local.audit_logs.kubernetes_cluster_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_storage_account_id
    reference_id         = local.audit_logs.kubernetes_cluster_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_storage_account_id
    reference_id         = local.audit_logs.kubernetes_cluster_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Api Management

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_log_analytics_id
    reference_id         = local.audit_logs.api_management_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_storage_account_id
    reference_id         = local.audit_logs.api_management_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_storage_account_id
    reference_id         = local.audit_logs.api_management_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Postgresql Flexible

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_log_analytics_id
    reference_id         = local.audit_logs.postgresql_flexible_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_storage_account_id
    reference_id         = local.audit_logs.postgresql_flexible_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_storage_account_id
    reference_id         = local.audit_logs.postgresql_flexible_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Postgresql Flexible

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_log_analytics_id
    reference_id         = local.audit_logs.postgresql_single_server_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_storage_account_id
    reference_id         = local.audit_logs.postgresql_single_server_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_storage_account_id
    reference_id         = local.audit_logs.postgresql_single_server_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Log Analytics Workspace

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_log_analytics_id
    reference_id         = local.audit_logs.log_analytics_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_storage_account_id
    reference_id         = local.audit_logs.log_analytics_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_storage_account_id
    reference_id         = local.audit_logs.log_analytics_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Cosmos DB

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_log_analytics_id
    reference_id         = local.audit_logs.cosmos_db_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_storage_account_id
    reference_id         = local.audit_logs.cosmos_db_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_storage_account_id
    reference_id         = local.audit_logs.cosmos_db_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## App Service

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_log_analytics_id
    reference_id         = local.audit_logs.app_service_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_storage_account_id
    reference_id         = local.audit_logs.app_service_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_storage_account_id
    reference_id         = local.audit_logs.app_service_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Event Hub

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_log_analytics_id
    reference_id         = local.audit_logs.event_hub_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_storage_account_id
    reference_id         = local.audit_logs.event_hub_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_storage_account_id
    reference_id         = local.audit_logs.event_hub_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Public IP

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_log_analytics_id
    reference_id         = local.audit_logs.public_ip_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_storage_account_id
    reference_id         = local.audit_logs.public_ip_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_storage_account_id
    reference_id         = local.audit_logs.public_ip_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Virtual Network Gateway

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_log_analytics_id
    reference_id         = local.audit_logs.virtual_network_gateway_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_storage_account_id
    reference_id         = local.audit_logs.virtual_network_gateway_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_storage_account_id
    reference_id         = local.audit_logs.virtual_network_gateway_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

  ## Grafana

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_log_analytics_id
    reference_id         = local.audit_logs.grafana_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "[parameters('logAnalyticsId')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_storage_account_id
    reference_id         = local.audit_logs.grafana_storageid_westeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountPrimaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountPrimaryRegionLocation')]"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_storage_account_id
    reference_id         = local.audit_logs.grafana_storageid_northeurope_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "[parameters('storageAccountSecondaryRegionId')]"
      },
      "location": {
        "value": "[parameters('storageAccountSecondaryRegionLocation')]"
      }
    }
    VALUE
  }

}

output "audit_logs_pci_id" {
  value = azurerm_policy_set_definition.audit_logs_pci.id
}

output "audit_logs_pci_workspace_id" {
  value = var.audit_logs_pci_workspace_id
}

output "audit_logs_pci_storage_primary_region" {
  value = var.audit_logs_pci_storage_primary_region
}

output "audit_logs_pci_storage_secondary_region" {
  value = var.audit_logs_pci_storage_secondary_region
}
