resource "azurerm_subscription_policy_assignment" "audit_logs_pci" {
  name                 = substr("${local.prefix}auditlogspci", 0, 64)
  display_name         = "PagoPA PROD PCI Audit logs"
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
}

resource "azurerm_role_assignment" "audit_logs_monitoring_contributor" {
  scope                = var.subscription.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_subscription_policy_assignment.audit_logs_pci.identity[0].principal_id
}

resource "azurerm_role_assignment" "audit_logs_contributor_log_analytics" {
  scope                = var.audit_logs.workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_subscription_policy_assignment.audit_logs_pci.identity[0].principal_id
}

resource "azurerm_role_assignment" "audit_logs_contributor_storage_westeurope" {
  scope                = var.audit_logs.storage_primary_region_storage_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_subscription_policy_assignment.audit_logs_pci.identity[0].principal_id
}
