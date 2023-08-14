output "policy_ids" {
  value = [
    azurerm_policy_definition.allowed_locations_resource_group.id,
    azurerm_policy_definition.allowed_locations.id,
  ]
}

output "allowed_locations_resource_group_id" {
  value = azurerm_policy_definition.allowed_locations_resource_group.id
}

output "allowed_locations_id" {
  value = azurerm_policy_definition.allowed_locations.id
}
