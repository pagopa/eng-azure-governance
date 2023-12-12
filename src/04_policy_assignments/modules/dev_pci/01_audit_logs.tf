resource "azurerm_subscription_policy_assignment" "audit_logs" {
  name                 = substr("${local.prefix}auditlogs", 0, 64)
  display_name         = "PagoPA DEV PCI Audit logs"
  policy_definition_id = var.policy_set_ids.audit_logs_pci_id
  subscription_id      = var.subscription.id

  location = var.location
  enforce  = true
  identity {
    type = "SystemAssigned"
  }

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })

  parameters = jsonencode({
    logAnalyticsId = {
      value = var.audit_logs.workspace_id
    }
    storageAccountPrimaryRegionId = {
      value = var.audit_logs.storage_primary_region_storage_id
    }
    storageAccountPrimaryRegionLocation = {
      value = var.audit_logs.storage_primary_region_location
    }
    storageAccountSecondaryRegionId = {
      value = var.audit_logs.storage_secondary_region_storage_id
    }
    storageAccountSecondaryRegionLocation = {
      value = var.audit_logs.storage_secondary_region_location
    }
  })
}

resource "azurerm_role_assignment" "audit_logs_monitoring_contributor" {
  scope                = var.subscription.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_subscription_policy_assignment.audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "audit_logs_contributor_log_analytics" {
  scope                = var.audit_logs.workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "audit_logs_contributor_storage_westeurope" {
  scope                = var.audit_logs.storage_primary_region_storage_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.audit_logs.identity[0].principal_id
}
