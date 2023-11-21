resource "azurerm_subscription_policy_assignment" "networking" {
  name                 = substr("${local.prefix}networking", 0, 64)
  display_name         = "PagoPA PROD Networking"
  policy_definition_id = var.policy_set_ids.networking_prod_id
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

resource "azurerm_role_assignment" "network_contributor" {
  scope                = var.subscription.id
  role_definition_name = "Network Contributor"
  principal_id         = azurerm_subscription_policy_assignment.networking.identity[0].principal_id
}

resource "azurerm_role_assignment" "network_contributor_ddosplan" {
  scope                = "/subscriptions/0da48c97-355f-4050-a520-f11a18b8be90/resourceGroups/sec-p-ddos/providers/Microsoft.Network/ddosProtectionPlans/sec-p-ddos-protection"
  role_definition_name = "Network Contributor"
  principal_id         = azurerm_subscription_policy_assignment.networking.identity[0].principal_id
}
