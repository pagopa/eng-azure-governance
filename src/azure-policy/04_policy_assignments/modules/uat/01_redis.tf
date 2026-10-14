resource "azurerm_subscription_policy_assignment" "redis" {
  name                 = substr("${local.prefix}redis", 0, 64)
  display_name         = "PagoPA UAT Redis"
  policy_definition_id = var.policy_set_ids.redis_uat_id
  subscription_id      = var.subscription.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
