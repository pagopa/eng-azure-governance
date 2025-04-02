output "policy_ids" {
  value = [
    azurerm_policy_definition.cosmosdb_required_network.id,
    azurerm_policy_definition.cosmosdb_allowed_tls.id,
    azurerm_policy_definition.cosmosdb_required_backup_policy.id,
    azurerm_policy_definition.cosmosdb_required_primary_zone_redundancy.id,
    azurerm_policy_definition.cosmosdb_forbidden_secondary_zone_redundancy.id,
    azurerm_policy_definition.cosmosdb_dynamic_scaling_enabled.id,
    azurerm_policy_definition.cosmosdb_automatic_failover_enabled.id,
    azurerm_policy_definition.cosmosdb_allowed_capacity_mode.id
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

output "cosmosdb_required_primary_zone_redundancy_id" {
  value = azurerm_policy_definition.cosmosdb_required_primary_zone_redundancy.id
}

output "cosmosdb_forbidden_secondary_zone_redundancy_id" {
  value = azurerm_policy_definition.cosmosdb_forbidden_secondary_zone_redundancy.id
}

output "cosmosdb_dynamic_scaling_enabled_id" {
  value = azurerm_policy_definition.cosmosdb_dynamic_scaling_enabled.id
}

output "cosmosdb_automatic_failover_enabled_id" {
  value = azurerm_policy_definition.cosmosdb_automatic_failover_enabled.id
}

output "cosmosdb_allowed_capacity_mode_id" {
  value = azurerm_policy_definition.cosmosdb_allowed_capacity_mode.id
}
