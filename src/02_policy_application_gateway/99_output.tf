output "policy_ids" {
  value = [
    azurerm_policy_definition.application_gateway_allowed_sku.id,
    azurerm_policy_definition.application_gateway_allowed_ciphersuites.id,
  ]
}

output "application_gateway_allowed_sku_id" {
  value = azurerm_policy_definition.application_gateway_allowed_sku.id
}

output "application_gateway_allowed_ciphersuites_id" {
  value = azurerm_policy_definition.application_gateway_allowed_ciphersuites.id
}
