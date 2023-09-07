output "policy_ids" {
  value = [
    data.azurerm_policy_definition.api_management_allowed_sku.id,
  ]
}

output "api_management_allowed_sku_id" {
  value = data.azurerm_policy_definition.api_management_allowed_sku.id
}
