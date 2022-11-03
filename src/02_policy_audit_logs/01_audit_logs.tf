data "azurerm_role_definition" "diagnostic_settings_contributor" {
  name = "PagoPA Resource Lock Contributor"
}

resource "azurerm_policy_definition" "audit_logs_keyvault" {
  name                = "pagopa_audit_logs_keyvault"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Add Diagnostic Settings for audit logs for KeyVault_vaults"
  management_group_id = data.azurerm_management_group.root_pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Add Diagnostic Settings for audit logs for KeyVault_vaults",
		      "Severity": "High"
        }
    }
METADATA

  parameters = <<PARAMETERS
  {
    "diagnosticsSettingNameToUse": {
      "type": "String",
      "metadata": {
        "displayName": "Setting name",
        "description": "Name of the diagnostic settings."
      },
      "defaultValue": "AuditLogs"
    },
    "logAnalytics": {
      "type": "String",
      "metadata": {
        "displayName": "Log Analytics workspace",
        "description": "Specify the Log Analytics workspace the Key Vault should be connected to.",
        "strongType": "omsWorkspace",
        "assignPermissions": true
      }
    },
    "storageAccount": {
      "type": "String",
      "metadata": {
        "displayName": "Storage Account",
        "description": "Specify the Storage Account the Key Vault should be connected to.",
        "assignPermissions": true
      }
    }
  }
PARAMETERS

  policy_rule = templatefile("./policy_rules/audit_logs/keyvault.json", {
    host = "pippo"
  })

}
