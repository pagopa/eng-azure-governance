resource "azurerm_subscription_policy_assignment" "container_apps" {
  name                 = substr("${local.prefix}containerapps", 0, 64)
  display_name         = "PagoPA PROD Container Apps"
  policy_definition_id = var.policy_set_ids.container_apps_prod_id
  subscription_id      = var.subscription.id
  enforce              = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
