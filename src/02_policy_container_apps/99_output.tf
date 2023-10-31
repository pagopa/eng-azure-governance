output "policy_ids" {
  value = [
    azurerm_policy_definition.enforce_multiaz.id,
  ]
}

output "enforce_multiaz_id" {
  value = azurerm_policy_definition.enforce_multiaz.id
}
