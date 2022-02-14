locals {
  list_allowed_locations_prod = jsonencode(var.prod_allowed_locations)
  list_allow_skus_raw_prod = jsonencode(var.prod_vm_skus_allowed)
}

resource "azurerm_management_group_policy_assignment" "prod_set_2_root_sl_pay" {
  name                 = "pa_prodset2root_sl_pay"
  display_name = "PagoPA/PROD set 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.prod_set.id
  management_group_id  = data.azurerm_management_group.prod_sl_pagamenti_servizi.id

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
          "value": ${local.list_allowed_locations_prod}
      },
      "listOfAllowedSKUs": {
          "value": ${local.list_allow_skus_raw_prod}
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}
