output "policy_ids" {
  value = concat(
    [for tags_inherit_from_subscription in azurerm_policy_definition.tags_inherit_from_subscription : tags_inherit_from_subscription.id],
    azurerm_policy_definition.require_tag.id,
    azurerm_policy_definition.require_tag_values.id,
  )
}

output "tags_require_tag_id" {
  value = azurerm_policy_definition.require_tag.id
}

output "tags_require_tag_values_id" {
  value = azurerm_policy_definition.require_tag_values.id
}