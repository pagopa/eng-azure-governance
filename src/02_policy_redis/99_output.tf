output "policy_ids" {
  value = [
    azurerm_policy_definition.redis_allowed_versions.id,
    azurerm_policy_definition.redis_allowed_tls.id,
    azurerm_policy_definition.redis_disable_nosslport.id,
    azurerm_policy_definition.redis_allowed_sku.id,
    # azurerm_policy_definition.redis_required_zone_redundant.id,
  ]
}

output "redis_allowed_versions_id" {
  value = azurerm_policy_definition.redis_allowed_versions.id
}

output "redis_allowed_tls_id" {
  value = azurerm_policy_definition.redis_allowed_tls.id
}

output "redis_disable_nosslport_id" {
  value = azurerm_policy_definition.redis_disable_nosslport.id
}

output "redis_allowed_sku_id" {
  value = azurerm_policy_definition.redis_allowed_sku.id
}
