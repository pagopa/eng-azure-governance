output "policy_ids" {
  value = [
    azurerm_policy_definition.audit_logs_keyvault.id,
  ]
}
