locals {
  list_allowed_locations_uat = jsonencode(var.uat_allowed_locations)
  list_allow_skus_raw_uat = jsonencode(var.uat_vm_skus_allowed)
}

resource "azurerm_management_group_policy_assignment" "uat_set_2_root_sl_pay" {
  name                 = "pa_uatset2root_sl_pay"
  display_name = "PagoPA/UAT set 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.uat_set.id
  management_group_id  = data.azurerm_management_group.uat_sl_pagamenti_servizi.id

  location = var.location
  enforce = false

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  parameters = <<PARAMS
  {
      "listOfAllowedLocations": {
          "value": ${local.list_allowed_locations_uat}
      },
      "listOfAllowedSKUs": {
          "value": ${local.list_allow_skus_raw_uat}
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}
