output "policy_ids" {
  value = [
    for resource_lock in azurerm_policy_definition.resource_lock : resource_lock.id
  ]
}
