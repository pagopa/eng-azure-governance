resource "azurerm_subscription_policy_assignment" "metrics_logs" {
  name                 = substr("${local.prefix}metricslogs", 0, 64)
  display_name         = "PagoPA DEV PCI Metric logs"
  policy_definition_id = var.policy_set_ids.metrics_logs_id
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
      value = var.metrics_logs.workspace_id
    }
  })
}

resource "azurerm_role_assignment" "dev_pci_metrics_logs_monitoring_contributor" {
  scope                = var.subscription.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_subscription_policy_assignment.metrics_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "dev_pci_metrics_logs_contributor_log_analytics" {
  scope                = var.metrics_logs.workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_subscription_policy_assignment.metrics_logs.identity[0].principal_id
}
