locals {
  list_allowed_locations_dev = jsonencode(var.dev_allowed_locations)
  list_allow_skus_raw_dev    = jsonencode(var.dev_vm_skus_allowed)
}

resource "azurerm_management_group_policy_assignment" "dev_set_2_root_sl_pay" {
  name                 = "pa_devset2root_sl_pay"
  display_name         = "PagoPA/Dev set 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.dev_set.id
  management_group_id  = data.azurerm_management_group.dev_sl_pagamenti_servizi.id

  location = var.location
  enforce  = false

  metadata = <<METADATA
  {
      "category": "${var.metadata_category_name}",
      "version": "v1.0.0"
  }
METADATA

  parameters = <<PARAMS
  {
      "listOfAllowedLocations": {
          "value": ${local.list_allowed_locations_dev}
      },
      "listOfAllowedSKUs": {
          "value": ${local.list_allow_skus_raw_dev}
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}
