resource "azurerm_subscription_policy_assignment" "audit_logs" {
  name                 = substr("${local.prefix}auditlogs", 0, 64)
  display_name         = "PagoPA PROD Audit logs"
  policy_definition_id = var.policy_set_ids.audit_logs_id
  subscription_id      = var.subscription.id
  location             = var.location
  enforce              = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "audit_logs_monitoring_contributor" {
  scope                = var.subscription.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_subscription_policy_assignment.audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "audit_logs_contributor_log_analytics" {
  scope                = var.policy_set_ids.audit_logs_workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_subscription_policy_assignment.audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "audit_logs_contributor_storage_westeurope" {
  scope                = var.policy_set_ids.audit_logs_storage_id_westeurope
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_subscription_policy_assignment.audit_logs.identity[0].principal_id
}
