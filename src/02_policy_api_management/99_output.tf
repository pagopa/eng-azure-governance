output "policy_ids" {
  value = [
    azurerm_policy_definition.api_management_allowed_versions.id,
  ]
}

output "api_management_allowed_versions_id" {
  value = azurerm_policy_definition.api_management_allowed_versions.id
}
