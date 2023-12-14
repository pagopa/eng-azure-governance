resource "azurerm_subscription_policy_assignment" "cosmosdb" {
  name                 = substr("${local.prefix}cosmosdb", 0, 64)
  display_name         = "PagoPA PROD CosmosDB"
  policy_definition_id = var.policy_set_ids.cosmosdb_prod_id
  subscription_id      = var.subscription.id
  enforce              = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
