resource "azurerm_management_group_policy_assignment" "root_set_2_root_sl_pay" {
  name                 = "pa_rootset2root_sl_pay"
  display_name         = "PagoPA/Root set 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.root_set.id
  management_group_id  = data.azurerm_management_group.root_sl_pagamenti_servizi.id

  location = var.location
  enforce  = false

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  identity {
    type = "SystemAssigned"
  }
}
