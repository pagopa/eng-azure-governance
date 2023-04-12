output "policy_ids" {
  value = [
    azurerm_policy_definition.eventhub_required_network.id,
  ]
}

output "eventhub_required_network_id" {
  value = azurerm_policy_definition.eventhub_required_network.id
}
