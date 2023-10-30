output "policy_ids" {
  value = [
    azurerm_policy_definition.network_deny_zonal_publicip.id,
  ]
}

output "network_deny_zonal_publicip" {
  value = azurerm_policy_definition.network_deny_zonal_publicip.id
}
