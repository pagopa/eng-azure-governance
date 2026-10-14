output "policy_ids" {
  value = [
    azurerm_policy_definition.enforce_multiaz.id,
    azurerm_policy_definition.min_execution.id
  ]
}

output "enforce_multiaz_id" {
  value = azurerm_policy_definition.enforce_multiaz.id
}

output "min_execution_id" {
  value = azurerm_policy_definition.min_execution.id
}
