resource "azurerm_subscription_policy_assignment" "pcidssv4" {
  name                 = substr("${local.prefix}pcidssv4", 0, 64)
  display_name         = "PCI DSS v4"
  policy_definition_id = "/providers/Microsoft.Authorization/policySetDefinitions/c676748e-3af9-4e22-bc28-50feed564afb"
  subscription_id      = var.subscription.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}
