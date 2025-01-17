output "policy_ids" {
  value = [
    azurerm_policy_definition.log_analytics_bound_daily_quota.id,
    azurerm_policy_definition.log_analytics_unbound_daily_quota.id,
    azurerm_policy_definition.log_analytics_link_dedicated_cluster.id,
  ]
}

output "log_analytics_bound_daily_quota_id" {
  value = azurerm_policy_definition.log_analytics_bound_daily_quota.id
}

output "log_analytics_unbound_daily_quota_id" {
  value = azurerm_policy_definition.log_analytics_unbound_daily_quota.id
}

output "log_analytics_link_dedicated_cluster_id" {
  value = azurerm_policy_definition.log_analytics_link_dedicated_cluster.id
}
