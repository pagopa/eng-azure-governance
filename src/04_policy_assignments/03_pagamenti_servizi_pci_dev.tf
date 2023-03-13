data "azurerm_management_group" "pagamenti_servizi_pci_dev" {
  name = "pagamenti_servizi_pci_dev"
}

locals {
  pagamenti_servizi_pci_dev_prefix = "pcid"
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_pci_dev_pcidssv4" {
  name                 = "${local.pagamenti_servizi_pci_dev_prefix}pcidssv4"
  display_name         = "PCI DSS v4"
  policy_definition_id = local.pci_dss_v4.id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_pci_dev.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_pci_dev_iso_27001_2013" {
  name                 = "${local.pagamenti_servizi_pci_dev_prefix}iso270012013"
  display_name         = "ISO 27001:2013"
  policy_definition_id = local.iso_27001_2013.id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_pci_dev.id

  parameters = jsonencode(
    {
      metricsEnabled-7f89b1eb-583c-429a-8828-af049802c1d9 = {
        value = false
      }
    }
  )

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}
