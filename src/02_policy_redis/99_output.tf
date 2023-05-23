output "policy_ids" {
  value = [
    azurerm_policy_definition.redis_allowed_versions.id,
    # azurerm_policy_definition.redis_required_zone_redundant.id,
  ]
}

output "redis_allowed_versions_id" {
  value = azurerm_policy_definition.redis_allowed_versions.id
}
