output "policy_ids" {
  value = [
    azurerm_policy_definition.audit_logs_keyvault_log_analytics.id,
    azurerm_policy_definition.audit_logs_keyvault_storage_account.id,
    azurerm_policy_definition.audit_logs_application_gateway_log_analytics.id,
    azurerm_policy_definition.audit_logs_application_gateway_storage_account.id,
    azurerm_policy_definition.audit_logs_container_registry_log_analytics.id,
    azurerm_policy_definition.audit_logs_container_registry_storage_account.id,
    azurerm_policy_definition.audit_logs_kubernetes_cluster_log_analytics.id,
    azurerm_policy_definition.audit_logs_kubernetes_cluster_storage_account.id,
    azurerm_policy_definition.audit_logs_api_management_log_analytics.id,
    azurerm_policy_definition.audit_logs_api_management_storage_account.id,
    azurerm_policy_definition.audit_logs_postgresql_flexible_log_analytics.id,
    azurerm_policy_definition.audit_logs_postgresql_flexible_storage_account.id,
    azurerm_policy_definition.audit_logs_postgresql_single_server_log_analytics.id,
    azurerm_policy_definition.audit_logs_postgresql_single_server_storage_account.id,
  ]
}

output "audit_logs_keyvault_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_keyvault_log_analytics.id
}

output "audit_logs_keyvault_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_keyvault_storage_account.id
}

output "audit_logs_application_gateway_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_application_gateway_log_analytics.id
}

output "audit_logs_application_gateway_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_application_gateway_storage_account.id
}

output "audit_logs_container_registry_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_container_registry_log_analytics.id
}

output "audit_logs_container_registry_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_container_registry_storage_account.id
}

output "audit_logs_kubernetes_cluster_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_kubernetes_cluster_log_analytics.id
}

output "audit_logs_kubernetes_cluster_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_kubernetes_cluster_storage_account.id
}

output "audit_logs_api_management_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_api_management_log_analytics.id
}

output "audit_logs_api_management_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_api_management_storage_account.id
}

output "audit_logs_postgresql_flexible_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_postgresql_flexible_log_analytics.id
}

output "audit_logs_postgresql_flexible_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_postgresql_flexible_storage_account.id
}

output "audit_logs_postgresql_single_server_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_postgresql_single_server_log_analytics.id
}

output "audit_logs_postgresql_single_server_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_postgresql_single_server_storage_account.id
}

output "audit_logs_log_analytics_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_log_analytics_log_analytics.id
}

output "audit_logs_log_analytics_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_log_analytics_storage_account.id
}

output "audit_logs_cosmos_db_log_analytics_id" {
  value = azurerm_policy_definition.audit_logs_cosmos_db_log_analytics.id
}

output "audit_logs_cosmos_db_storage_account_id" {
  value = azurerm_policy_definition.audit_logs_cosmos_db_storage_account.id
}
