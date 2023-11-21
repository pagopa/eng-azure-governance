resource "azurerm_subscription_policy_assignment" "application_gateway" {
  name                 = substr("${local.prefix}applicationgateway", 0, 64)
  display_name         = "PagoPA PROD Application Gateway"
  policy_definition_id = var.policy_set_ids.application_gateway_prod_id
  subscription_id      = var.subscription.id
  enforce              = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
