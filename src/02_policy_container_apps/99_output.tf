output "policy_ids" {
  value = [
    azurerm_policy_definition.container_apps_enforce_multiaz.id,
  ]
}

output "container_apps_enforce_multiaz_id" {
  value = azurerm_policy_definition.container_apps_enforce_multiaz.id
}
