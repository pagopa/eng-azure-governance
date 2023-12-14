resource "azurerm_subscription_policy_assignment" "api_management" {
  name                 = substr("${local.prefix}apimanagement", 0, 64)
  display_name         = "PagoPA DEV Api Management"
  policy_definition_id = var.policy_set_ids.api_management_dev_id
  subscription_id      = var.subscription.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
