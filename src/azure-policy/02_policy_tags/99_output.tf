output "policy_ids" {
  value = [
    azurerm_policy_definition.require_tag.id,
    azurerm_policy_definition.require_tag_values.id,
  ]
}

output "tags_require_tag_id" {
  value = azurerm_policy_definition.require_tag.id
}

output "tags_require_tag_values_id" {
  value = azurerm_policy_definition.require_tag_values.id
}
