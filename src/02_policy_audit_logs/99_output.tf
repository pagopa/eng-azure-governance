output "policy_ids" {
  value = [
    azurerm_policy_definition.audit_logs_keyvault_log_analytics.id,
    azurerm_policy_definition.audit_logs_keyvault_storage_account.id,
  ]
}

output "audit_logs_keyvault_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_keyvault_log_analytics.id
}

output "audit_logs_keyvault_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_keyvault_storage_account.id
}
