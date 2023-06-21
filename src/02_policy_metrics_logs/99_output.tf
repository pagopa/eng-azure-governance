output "policy_ids" {
  value = [
    for metrics_logs in azurerm_policy_definition.metrics_logs : metrics_logs.id
  ]
}
