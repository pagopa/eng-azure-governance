output "policy_ids" {
  value = [
    for tags_inherit_from_subscription in azurerm_policy_definition.tags_inherit_from_subscription : tags_inherit_from_subscription.id
  ]
}
