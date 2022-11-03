# data "azurerm_role_definition" "diagnostic_settings_contributor" {
#   name = "PagoPA Resource Lock Contributor"
# }

resource "azurerm_policy_definition" "audit_logs_keyvault_log_analytics" {
  name                = "audit_logs_keyvault_log_analytics"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Add Diagnostic Settings for audit logs for KeyVault to Log Analytics workspace"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Add Diagnostic Settings for audit logs for KeyVault to Log Analytics workspace",
		      "Severity": "High"
        }
    }
METADATA

  parameters = <<PARAMETERS
  {
    "diagnosticsSettingName": {
      "type": "String",
      "metadata": {
        "displayName": "Setting name",
        "description": "Name of the diagnostic settings."
      },
      "defaultValue": "AuditLogs_LogAnalytics"
    },
    "logAnalytics": {
      "type": "String",
      "metadata": {
        "displayName": "Log Analytics workspace",
        "description": "Specify the Log Analytics workspace the Key Vault should be connected to.",
        "strongType": "omsWorkspace",
        "assignPermissions": true
      }
    }
  }
PARAMETERS

  policy_rule = templatefile("./policy_rules/keyvault_log_analytics.json", {
    host = "pippo"
  })

}

resource "azurerm_policy_definition" "audit_logs_keyvault_storage_account" {
  name                = "audit_logs_keyvault_storage_account"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Add Diagnostic Settings for audit logs for KeyVault to Storage Account"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Add Diagnostic Settings for audit logs for KeyVault to Storage Account",
		      "Severity": "High"
        }
    }
METADATA

  parameters = <<PARAMETERS
  {
    "diagnosticsSettingName": {
      "type": "String",
      "metadata": {
        "displayName": "Setting name",
        "description": "Name of the diagnostic settings."
      },
      "defaultValue": "AuditLogs_StorageAccount"
    },
    "storageAccount": {
      "type": "String",
      "metadata": {
        "displayName": "Storage Account",
        "description": "Specify the Storage Account the Key Vault should be connected to.",
        "assignPermissions": true
      }
    },
    "location": {
      "type": "String",
      "metadata": {
        "displayName": "Resource location",
        "description": "Specify the resource location.",
        "assignPermissions": true
      }
    }
  }
PARAMETERS

  policy_rule = templatefile("./policy_rules/keyvault_storage_account.json", {
    host = "pippo"
  })

}
