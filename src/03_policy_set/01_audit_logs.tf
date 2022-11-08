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
  default     = "novalue"
  description = "description"
}

locals {
  audit_logs = {
    metadata_category_name                                 = "pagopa_env_prod"
    keyvault_workspaceid_reference_id                      = "keyvault_workspaceid"
    keyvault_storageid_westeurope_reference_id             = "keyvault_storageid_westeurope"
    keyvault_storageid_northeurope_reference_id            = "keyvault_storageid_northeurope"
    application_gateway_workspaceid_reference_id           = "application_gateway_workspaceid"
    application_gateway_storageid_westeurope_reference_id  = "application_gateway_storageid_westeurope"
    application_gateway_storageid_northeurope_reference_id = "application_gateway_storageid_northeurope"
    container_registry_workspaceid_reference_id            = "container_registry_workspaceid"
    container_registry_storageid_westeurope_reference_id   = "container_registry_storageid_westeurope"
    container_registry_storageid_northeurope_reference_id  = "container_registry_storageid_northeurope"
    kubernetes_cluster_workspaceid_reference_id            = "kubernetes_cluster_workspaceid"
    kubernetes_cluster_storageid_westeurope_reference_id   = "kubernetes_cluster_storageid_westeurope"
    kubernetes_cluster_storageid_northeurope_reference_id  = "kubernetes_cluster_storageid_northeurope"
    api_management_workspaceid_reference_id                = "api_management_workspaceid"
    api_management_storageid_westeurope_reference_id       = "api_management_storageid_westeurope"
    api_management_storageid_northeurope_reference_id      = "api_management_storageid_northeurope"
    postgresql_flexible_workspaceid_reference_id           = "postgresql_flexible_workspaceid"
    postgresql_flexible_storageid_westeurope_reference_id  = "postgresql_flexible_storageid_westeurope"
    postgresql_flexible_storageid_northeurope_reference_id = "postgresql_flexible_storageid_northeurope"
  }
}

resource "azurerm_policy_set_definition" "audit_logs" {
  name                = "audit_logs"
  policy_type         = "Custom"
  display_name        = "PagoPA Audit logs"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.audit_logs.metadata_category_name}",
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
          "${local.audit_logs.postgresql_flexible_storageid_northeurope_reference_id} : ${local.audit_logs.postgresql_flexible_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}"
        }
    }
METADATA

  ## Key vault

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_log_analytics_id
    reference_id         = local.audit_logs.keyvault_workspaceid_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "${var.audit_logs_workspace_id}"
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
        "value": "${var.audit_logs_storage_id_westeurope}"
      },
      "location": {
        "value": "westeurope"
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
        "value": "${var.audit_logs_storage_id_northeurope}"
      },
      "location": {
        "value": "northeurope"
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
        "value": "${var.audit_logs_workspace_id}"
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
        "value": "${var.audit_logs_storage_id_westeurope}"
      },
      "location": {
        "value": "westeurope"
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
        "value": "${var.audit_logs_storage_id_northeurope}"
      },
      "location": {
        "value": "northeurope"
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
        "value": "${var.audit_logs_workspace_id}"
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
        "value": "${var.audit_logs_storage_id_westeurope}"
      },
      "location": {
        "value": "westeurope"
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
        "value": "${var.audit_logs_storage_id_northeurope}"
      },
      "location": {
        "value": "northeurope"
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
        "value": "${var.audit_logs_workspace_id}"
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
        "value": "${var.audit_logs_storage_id_westeurope}"
      },
      "location": {
        "value": "westeurope"
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
        "value": "${var.audit_logs_storage_id_northeurope}"
      },
      "location": {
        "value": "northeurope"
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
        "value": "${var.audit_logs_workspace_id}"
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
        "value": "${var.audit_logs_storage_id_westeurope}"
      },
      "location": {
        "value": "westeurope"
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
        "value": "${var.audit_logs_storage_id_northeurope}"
      },
      "location": {
        "value": "northeurope"
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
        "value": "${var.audit_logs_workspace_id}"
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
        "value": "${var.audit_logs_storage_id_westeurope}"
      },
      "location": {
        "value": "westeurope"
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
        "value": "${var.audit_logs_storage_id_northeurope}"
      },
      "location": {
        "value": "northeurope"
      }
    }
    VALUE
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