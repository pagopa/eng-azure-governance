resource "azurerm_subscription_policy_assignment" "app_service" {
  name                 = substr("${local.prefix}appservice", 0, 64)
  display_name         = "PagoPA UAT App Service"
  policy_definition_id = var.policy_set_ids.app_service_uat_id
  subscription_id      = var.subscription.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
