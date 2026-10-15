output "policy_ids" {
  value = [
    azurerm_policy_definition.virtual_machine_allowed_sku.id,
  ]
}

output "virtual_machine_allowed_sku_id" {
  value = azurerm_policy_definition.virtual_machine_allowed_sku.id
}
