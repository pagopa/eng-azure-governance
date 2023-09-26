output "policy_ids" {
  value = [
    azurerm_policy_definition.postgres_required_flexible_georedundancy.id,
  ]
}

output "postgres_required_flexible_georedundancy_id" {
  value = azurerm_policy_definition.postgres_required_flexible_georedundancy.id
}
