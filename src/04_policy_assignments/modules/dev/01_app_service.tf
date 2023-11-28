resource "azurerm_subscription_policy_assignment" "app_service" {
  name                 = substr("${local.prefix}appservice", 0, 64)
  display_name         = "PagoPA App Service"
  policy_definition_id = var.policy_set_ids.app_service_dev_id
  subscription_id      = var.subscription.subscription_id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
