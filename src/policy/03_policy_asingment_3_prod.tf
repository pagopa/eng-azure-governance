locals {
  list_allowed_locations_prod = jsonencode(var.prod_allowed_locations)
  list_allow_skus_raw_prod    = jsonencode(var.prod_vm_skus_allowed)
}

resource "azurerm_management_group_policy_assignment" "prod_set_enforced_2_root_sl_pay" {
  name                 = "pa_prodsetenf2rootslpay"
  display_name         = "PagoPA/PROD set enforce 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.prod_set_enforced.id
  management_group_id  = data.azurerm_management_group.prod_sl_pagamenti_servizi.id

  location = var.location
  enforce  = true

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
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_assignment" "prod_set_advice_2_root_sl_pay" {
  name                 = "pa_prodsetadv2rootslpay"
  display_name         = "PagoPA/PROD set advice 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.prod_set_advice.id
  management_group_id  = data.azurerm_management_group.prod_sl_pagamenti_servizi.id

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
      "listOfAllowedSKUs": {
          "value": ${local.list_allow_skus_raw_prod}
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}
