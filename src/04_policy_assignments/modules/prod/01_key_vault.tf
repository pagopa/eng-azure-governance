resource "azurerm_subscription_policy_assignment" "key_vault" {
  name                 = substr("${local.prefix}keyvault", 0, 64)
  display_name         = "PagoPA PROD Key Vault"
  policy_definition_id = var.policy_set_ids.key_vault_prod_id
  subscription_id      = var.subscription.id
  enforce              = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
