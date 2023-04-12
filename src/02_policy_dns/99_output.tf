output "policy_ids" {
  value = [
    azurerm_policy_definition.dns_required_caa_record.id,
  ]
}

output "dns_required_caa_record_id" {
  value = azurerm_policy_definition.dns_required_caa_record.id
}
