output "policy_ids" {
  value = [
    azurerm_policy_definition.cosmosdb_required_network.id,
    azurerm_policy_definition.cosmosdb_allowed_tls.id,
  ]
}

output "cosmosdb_required_network_id" {
  value = azurerm_policy_definition.cosmosdb_required_network.id
}

output "cosmosdb_allowed_tls_id" {
  value = azurerm_policy_definition.cosmosdb_allowed_tls.id
}
