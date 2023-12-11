resource "azurerm_policy_definition" "audit_logs_postgresql_single_server_log_analytics" {
  name                = "audit_logs_postgresql_single_server_log_analytics"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Add Diagnostic Settings for audit logs for Postgresql Single Server to Log Analytics workspace"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Add Diagnostic Settings for audit logs for Postgresql Single Server to Log Analytics workspace"
      Severity               = "High"
    }
  })

  parameters = jsonencode({
    diagnosticsSettingName = {
      type = "String"
      metadata = {
        displayName = "Setting name"
        description = "Name of the diagnostic settings."
      }
      defaultValue = "AuditLogs_LogAnalytics"
    }
    logAnalytics = {
      type = "String"
      metadata = {
        displayName       = "Log Analytics workspace"
        description       = "Specify the Log Analytics workspace the Key Vault should be connected to."
        strongType        = "omsWorkspace"
        assignPermissions = true
      }
    }
  })

  policy_rule = templatefile("./policy_rules/postgresql_single_server_log_analytics.json", {
    roleDefinitionIds_audit_logs_contributor    = data.azurerm_role_definition.audit_logs_contributor.id,
    roleDefinitionIds_log_analytics_contributor = data.azurerm_role_definition.log_analytics_contributor.id,
  })

}

resource "azurerm_policy_definition" "audit_logs_postgresql_single_server_storage_account" {
  name                = "audit_logs_postgresql_single_server_storage_account"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Add Diagnostic Settings for audit logs for Postgresql Single Server to Storage Account"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Add Diagnostic Settings for audit logs for Postgresql Single Server to Storage Account"
      Severity               = "High"
    }
  })

  parameters = jsonencode({
    diagnosticsSettingName = {
      type = "String"
      metadata = {
        displayName = "Setting name"
        description = "Name of the diagnostic settings."
      }
      defaultValue = "AuditLogs_StorageAccount"
    }
    storageAccount = {
      type = "String"
      metadata = {
        displayName       = "Storage Account"
        description       = "Specify the Storage Account the Key Vault should be connected to."
        assignPermissions = true
      }
    }
    location = {
      type = "String"
      metadata = {
        displayName       = "Resource location"
        description       = "Specify the resource location."
        assignPermissions = true
      }
    }
  })

  policy_rule = templatefile("./policy_rules/postgresql_single_server_storage_account.json", {
    roleDefinitionIds_audit_logs_contributor    = data.azurerm_role_definition.audit_logs_contributor.id,
    roleDefinitionIds_log_analytics_contributor = data.azurerm_role_definition.log_analytics_contributor.id,
  })

}
