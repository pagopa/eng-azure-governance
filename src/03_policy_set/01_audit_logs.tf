variable "audit_logs_workspace_id" {
  type    = string
  default = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"
}

variable "audit_logs_storage_ids" {
  type = map(string)
  default = {
    westeurope  = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"
    northeurope = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-rg-neu/providers/Microsoft.Storage/storageAccounts/ppseclogsneu"
    italynorth  = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-rg-nit/providers/Microsoft.Storage/storageAccounts/ppseclogsitn"
  }
}

variable "audit_logs_storage_regions" {
  type    = list(string)
  default = ["westeurope", "northeurope", "italynorth"]
}

locals {
  audit_logs = {
    reference_ids = {
      api_management           = "api_management"
      app_service              = "app_service"
      application_gateway      = "application_gateway"
      container_registry       = "container_registry"
      cosmos_db                = "cosmos_db"
      event_hub                = "event_hub"
      grafana                  = "grafana"
      keyvault                 = "keyvault"
      kubernetes_cluster       = "kubernetes_cluster"
      log_analytics            = "log_analytics_server"
      postgresql_flexible      = "postgresql_flexible"
      postgresql_single_server = "postgresql_single_server"
      public_ip                = "public_ip"
      subscription             = "subscription_westeurope"
      virtual_network_gateway  = "virtual_network_gateway"
    }
  }
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
      for _, param in local.audit_logs.reference_ids : "${param} : ${param}" => data.azurerm_management_group.pagopa.id
    }
  })

  ## Workspace
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.keyvault}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.container_registry}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  # policy_definition_reference {
  #   policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_log_analytics_id
  #   reference_id         = "${local.audit_logs.reference_ids.kubernetes_cluster}_workspaceid"
  #   parameter_values = jsonencode({
  #     logAnalytics = {
  #       value = var.audit_logs_workspace_id
  #     }
  #   })
  # }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.api_management}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.postgresql_flexible}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.postgresql_single_server}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.log_analytics}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.cosmos_db}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.app_service}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.event_hub}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.public_ip}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.virtual_network_gateway}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.grafana}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_subscription_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.subscription}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_log_analytics_id
    reference_id         = "${local.audit_logs.reference_ids.application_gateway}_workspaceid"
    parameter_values = jsonencode({
      logAnalytics = {
        value = var.audit_logs_workspace_id
      }
    })
  }

  ## Storage
  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.keyvault}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_application_gateway_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.application_gateway}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_container_registry_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.container_registry}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  # policy_definition_reference {
  #   for_each = var.audit_logs_storage_regions
  #
  #   content {
  #     policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_kubernetes_cluster_storage_account_id
  #     reference_id         = "${local.audit_logs.reference_ids.kubernetes_cluster}_storageid_${policy_definition_reference.value}"
  #     parameter_values = jsonencode({
  #       storageAccount = {
  #         value = var.audit_logs_storage_ids[policy_definition_reference.value]
  #       }
  #       location = {
  #         value = "westeurope"
  #       }
  #     })
  #   }
  # }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_api_management_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.api_management}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_flexible_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.postgresql_flexible}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_postgresql_single_server_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.postgresql_single_server}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_log_analytics_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.log_analytics}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_cosmos_db_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.cosmos_db}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_app_service_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.app_service}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_event_hub_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.event_hub}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_public_ip_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.public_ip}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_virtual_network_gateway_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.virtual_network_gateway}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  dynamic "policy_definition_reference" {
    for_each = var.audit_logs_storage_regions

    content {
      policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_grafana_storage_account_id
      reference_id         = "${local.audit_logs.reference_ids.grafana}_storageid_${policy_definition_reference.value}"
      parameter_values = jsonencode({
        storageAccount = {
          value = var.audit_logs_storage_ids[policy_definition_reference.value]
        }
        location = {
          value = policy_definition_reference.value
        }
      })
    }
  }

  # Subscription logs must be send to west europe storage account
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_subscription_storage_account_id
    reference_id         = "${local.audit_logs.reference_ids.subscription}_storageid_westeurope"
    parameter_values = jsonencode({
      storageAccount = {
        value = var.audit_logs_storage_ids.westeurope
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
  value = var.audit_logs_storage_ids.westeurope
}

output "audit_logs_storage_id_northeurope" {
  value = var.audit_logs_storage_ids.northeurope
}

output "audit_logs_storage_id_italynorth" {
  value = var.audit_logs_storage_ids.italynorth
}
