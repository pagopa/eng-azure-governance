output "policy_ids" {
  value = [
    azurerm_policy_definition.app_service_allowed_linuxfxversion.id,
  ]
}

output "app_service_allowed_linuxfxversion_id" {
  value = azurerm_policy_definition.app_service_allowed_linuxfxversion.id
}
