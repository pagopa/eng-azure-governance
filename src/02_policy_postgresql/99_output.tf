output "policy_ids" {
  value = [
    azurerm_policy_definition.postgresql_required_flexible_georedundancy.id,
    azurerm_policy_definition.postgresql_required_engine_version.id,
    azurerm_policy_definition.postgresql_allowed_flexible_sku.id,
    azurerm_policy_definition.postgresql_allowed_sku.id,
  ]
}

output "postgresql_required_engine_version_id" {
  value = azurerm_policy_definition.postgresql_required_engine_version.id
}

output "postgresql_required_flexible_georedundancy_id" {
  value = azurerm_policy_definition.postgresql_required_flexible_georedundancy.id
}

output "postgresql_allowed_flexible_sku_id" {
  value = azurerm_policy_definition.postgresql_allowed_flexible_sku.id
}

output "postgresql_allowed_sku_id" {
  value = azurerm_policy_definition.postgresql_allowed_sku.id
}
