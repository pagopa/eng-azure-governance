variable "audit_logs_workspaceid" {
  type        = string
  default     = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourcegroups/sec-p-sentinel/providers/microsoft.operationalinsights/workspaces/sec-p-law"
  description = "description"
}

variable "audit_logs_storageid_westeurope" {
  type        = string
  default     = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-sentinel/providers/Microsoft.Storage/storageAccounts/ppseclogs"
  description = "description"
}

variable "audit_logs_storageid_northeurope" {
  type        = string
  default     = "novalue"
  description = "description"
}

locals {
  audit_logs = {
    workspaceid_policy_definition_reference_id           = "workspaceid"
    storageid_westeurope_policy_definition_reference_id  = "storageid_westeurope"
    storageid_northeurope_policy_definition_reference_id = "storageid_northeurope"
  }
}

resource "azurerm_policy_set_definition" "audit_logs" {
  name                = "audit_logs"
  policy_type         = var.policy_type
  display_name        = "PagoPA Audit logs to security"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "parameterScopes": {
          "workspaceid : ${local.audit_logs.workspaceid_policy_definition_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "storageid_westeurope : ${local.audit_logs.storageid_westeurope_policy_definition_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "storageid_northeurope : ${local.audit_logs.storageid_northeurope_policy_definition_reference_id}": "${data.azurerm_management_group.pagopa.id}"
        }
    }
METADATA

  ## Key vault

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_log_analytics_id
    reference_id         = local.audit_logs.workspaceid_policy_definition_reference_id
    parameter_values     = <<VALUE
    {
      "logAnalytics": {
        "value": "${var.audit_logs_workspaceid}"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
    reference_id         = local.audit_logs.storageid_westeurope_policy_definition_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "${var.audit_logs_storageid_westeurope}"
      },
      "location": {
        "value": "westeurope"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_audit_logs.outputs.audit_logs_keyvault_storage_account_id
    reference_id         = local.audit_logs.storageid_northeurope_policy_definition_reference_id
    parameter_values     = <<VALUE
    {
      "storageAccount": {
        "value": "${var.audit_logs_storageid_northeurope}"
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
