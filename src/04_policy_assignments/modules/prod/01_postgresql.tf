resource "azurerm_subscription_policy_assignment" "postgresql" {
  name                 = substr("${local.prefix}postgresql", 0, 64)
  display_name         = "PagoPA PROD PostgreSQL"
  policy_definition_id = var.policy_set_ids.postgresql_prod_id
  subscription_id      = var.subscription.id
  enforce              = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
