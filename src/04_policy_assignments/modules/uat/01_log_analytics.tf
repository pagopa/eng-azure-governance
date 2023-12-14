resource "azurerm_subscription_policy_assignment" "log_analytics" {
  name                 = substr("${local.prefix}loganalytics", 0, 64)
  display_name         = "PagoPA UAT Log Analytics"
  policy_definition_id = var.policy_set_ids.log_analytics_uat_id
  subscription_id      = var.subscription.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
