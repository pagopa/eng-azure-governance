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
    keyvault_workspaceid_reference_id                      = "keyvault_workspaceid"
    keyvault_storageid_westeurope_reference_id             = "keyvault_storageid_westeurope"
    keyvault_storageid_northeurope_reference_id            = "keyvault_storageid_northeurope"
    application_gateway_workspaceid_reference_id           = "application_gateway_workspaceid"
    application_gateway_storageid_westeurope_reference_id  = "application_gateway_storageid_westeurope"
    application_gateway_storageid_northeurope_reference_id = "application_gateway_storageid_northeurope"
  }
}

resource "azurerm_policy_set_definition" "audit_logs" {
  name                = "audit_logs"
  policy_type         = var.policy_type
  display_name        = "PagoPA Audit logs"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "parameterScopes": {
          "${local.audit_logs.keyvault_workspaceid_reference_id} : ${local.audit_logs.keyvault_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.keyvault_storageid_westeurope_reference_id} : ${local.audit_logs.keyvault_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.keyvault_storageid_northeurope_reference_id} : ${local.audit_logs.keyvault_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.application_gateway_workspaceid_reference_id} : ${local.audit_logs.application_gateway_workspaceid_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.application_gateway_storageid_westeurope_reference_id} : ${local.audit_logs.application_gateway_storageid_westeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "${local.audit_logs.application_gateway_storageid_northeurope_reference_id} : ${local.audit_logs.application_gateway_storageid_northeurope_reference_id}": "${data.azurerm_management_group.pagopa.id}"
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
