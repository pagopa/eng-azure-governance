resource "azurerm_subscription_policy_assignment" "storage_account" {
  name                 = substr("${local.prefix}stac", 0, 64)
  display_name         = "PagoPA PROD PCI Storage Account"
  policy_definition_id = var.policy_set_ids.storage_account_prod_id
  subscription_id      = var.subscription.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
