output "policy_ids" {
  value = [
    azurerm_policy_definition.eventhub_required_network.id,
    azurerm_policy_definition.eventhub_allowed_tls.id,
    azurerm_policy_definition.eventhub_required_zone_redundant.id,
  ]
}

output "eventhub_required_network_id" {
  value = azurerm_policy_definition.eventhub_required_network.id
}

output "eventhub_allowed_tls_id" {
  value = azurerm_policy_definition.eventhub_allowed_tls.id
}

output "eventhub_required_zone_redundant_id" {
  value = azurerm_policy_definition.eventhub_required_zone_redundant.id
}
