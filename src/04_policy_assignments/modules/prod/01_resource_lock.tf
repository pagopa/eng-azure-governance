resource "azurerm_subscription_policy_assignment" "resource_lock" {
  name                 = substr("${local.prefix}resourcelock", 0, 64)
  display_name         = "PagoPA PROD Resource lock"
  policy_definition_id = var.policy_set_ids.resource_lock_id
  subscription_id      = var.subscription.id
  location             = var.location
  enforce              = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "resource_lock_contributor" {
  scope                = var.subscription.id
  role_definition_name = "PagoPA Resource Lock Contributor"
  principal_id         = azurerm_subscription_policy_assignment.resource_lock.identity[0].principal_id
}

