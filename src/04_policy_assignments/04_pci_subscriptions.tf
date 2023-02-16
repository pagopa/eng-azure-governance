data "azurerm_subscriptions" "pci" {
  display_name_contains = "PCI"
}

resource "azurerm_subscription_policy_assignment" "subscription_pcidssv4" {
  for_each = { for s in data.azurerm_subscriptions.pci.subscriptions : s.display_name => s }

  name                 = "${lower(replace(each.value.display_name, "-", ""))}pcidssv4"
  display_name         = "PCI DSS v4"
  policy_definition_id = local.pci_dss_v4.id
  subscription_id      = each.value.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

output "subscriptions_pci" {
  value = data.azurerm_subscriptions.pci.subscriptions.*.display_name
}
