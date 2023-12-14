resource "azurerm_subscription_policy_assignment" "pcidssv4" {
  name                 = substr("${local.prefix}pcidssv4", 0, 64)
  display_name         = "PCI DSS v4"
  policy_definition_id = local.pci_dss_v4.id
  subscription_id      = var.subscription.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}
