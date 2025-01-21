output "policy_ids" {
  value = [
    azurerm_policy_definition.cosmosdb_required_network.id,
    azurerm_policy_definition.cosmosdb_allowed_tls.id,
    azurerm_policy_definition.cosmosdb_required_backup_policy.id,
    azurerm_policy_definition.cosmosdb_forbidden_capabilities.id,
    azurerm_policy_definition.cosmosdb_required_primary_zone_redundancy.id,
    azurerm_policy_definition.cosmosdb_forbidden_secondary_zone_redundancy.id,
    azurerm_policy_definition.cosmos_dynamic_scaling_enabled.id
  ]
}

output "cosmosdb_required_network_id" {
  value = azurerm_policy_definition.cosmosdb_required_network.id
}

output "cosmosdb_allowed_tls_id" {
  value = azurerm_policy_definition.cosmosdb_allowed_tls.id
}

output "cosmosdb_required_backup_policy_id" {
  value = azurerm_policy_definition.cosmosdb_required_backup_policy.id
}

output "cosmosdb_forbidden_capabilities_id" {
  value = azurerm_policy_definition.cosmosdb_forbidden_capabilities.id
}

output "cosmosdb_required_primary_zone_redundancy_id" {
  value = azurerm_policy_definition.cosmosdb_required_primary_zone_redundancy.id
}

output "cosmosdb_forbidden_secondary_zone_redundancy_id" {
  value = azurerm_policy_definition.cosmosdb_forbidden_secondary_zone_redundancy.id
}

output "cosmos_dynamic_scaling_enabled_id" {
  value = azurerm_policy_definition.cosmos_dynamic_scaling_enabled.id
}
