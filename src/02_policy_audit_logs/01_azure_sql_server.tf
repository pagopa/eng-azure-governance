resource "azurerm_policy_definition" "audit_logs_azure_sql_server_log_analytics" {
  name                = "audit_logs_azure_sql_server_log_analytics"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Add Diagnostic Settings for audit logs for Azure SQL Server to Log Analytics workspace"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Add Diagnostic Settings for audit logs for Azure SQL Server to Log Analytics workspace"
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
        description       = "Specify the Log Analytics workspace the Azure SQL Server should be connected to."
        strongType        = "omsWorkspace"
        assignPermissions = true
      }
    }
  })

  policy_rule = templatefile("./policy_rules/azure_sql_server_log_analytics.json", {
    roleDefinitionIds_sql_security_manager      = data.azurerm_role_definition.sql_security_manager.id,
    roleDefinitionIds_log_analytics_contributor = data.azurerm_role_definition.log_analytics_contributor.id,
  })

}

resource "azurerm_policy_definition" "audit_logs_azure_sql_server_storage_account" {
  name                = "audit_logs_azure_sql_server_storage_account"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Add Diagnostic Settings for audit logs for Azure SQL Server to Storage Account"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Add Diagnostic Settings for audit logs for Azure SQL Server to Storage Account"
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
    location = {
      type = "String"
      metadata = {
        displayName       = "Resource location"
        description       = "Specify the resource location."
        assignPermissions = true
      }
    }
    retentionDays = {
      type = "String"
      metadata = {
        displayName       = "Retention Days"
        description       = "Specify the Retention Days"
        assignPermissions = true
      }
    }
    storageAccountName = {
      type = "String"
      metadata = {
        displayName       = "Storage Account Name"
        description       = "Specify the Storage Account Name the Azure SQL Server should be connected to."
        assignPermissions = true
      }
    }
    storageAccountResourceGroup = {
      type = "String"
      metadata = {
        displayName       = "Storage Account Resource Group"
        description       = "Specify the Storage Account Resource Group the Azure SQL Server should be connected to."
        assignPermissions = true
      }
    }
    storageAccountSubscriptionId = {
      type = "String"
      metadata = {
        displayName       = "Storage Account Subscription Id"
        description       = "Specify the Storage Account Subscription Id the Azure SQL Server should be connected to."
        assignPermissions = true
      }
    }
  })

  policy_rule = templatefile("./policy_rules/azure_sql_server_storage_account.json", {
    roleDefinitionIds_sql_security_manager        = data.azurerm_role_definition.sql_security_manager.id,
    roleDefinitionIds_storage_account_contributor = data.azurerm_role_definition.storage_account_contributor.id,
  })

}
