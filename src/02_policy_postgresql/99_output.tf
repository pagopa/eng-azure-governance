output "policy_ids" {
  value = [
    azurerm_policy_definition.postgres_required_flexible_georedundancy.id,
  ]
}

output "postgres_required_flexible_georedundancy_id" {
  value = azurerm_policy_definition.postgres_required_flexible_georedundancy.id
}

output "postgres_allowed_flexible_sku_id" {
  value = azurerm_policy_definition.postgres_allowed_flexible_sku_id.id
}
