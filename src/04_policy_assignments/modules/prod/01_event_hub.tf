resource "azurerm_subscription_policy_assignment" "event_hub" {
  name                 = substr("${local.prefix}eventhub", 0, 64)
  display_name         = "PagoPA PROD EventHub"
  policy_definition_id = var.policy_set_ids.event_hub_prod_id
  subscription_id      = var.subscription.id
  enforce              = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
