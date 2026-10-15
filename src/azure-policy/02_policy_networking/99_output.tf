output "policy_ids" {
  value = [
    azurerm_policy_definition.deny_zonal_publicip.id,
  ]
}

output "deny_zonal_publicip_id" {
  value = azurerm_policy_definition.deny_zonal_publicip.id
}
