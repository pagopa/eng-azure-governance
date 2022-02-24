locals {
  list_allowed_locations_devops = jsonencode(var.devops_allowed_locations)
  list_allow_skus_raw_devops    = jsonencode(var.devops_vm_skus_allowed)
}

resource "azurerm_management_group_policy_assignment" "devops_set_enforced_2_root_sl_pay" {
  name                 = "pa_dvopsenf2rootslpay"
  display_name         = "PagoPA/DEVOPS set enforced 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.devops_set_enforced.id
  management_group_id  = data.azurerm_management_group.devops_sl_pagamenti_servizi.id

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
          "value": ${local.list_allowed_locations_devops}
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_assignment" "devops_set_advice_2_root_sl_pay" {
  name                 = "pa_dvopsadv2rootslpay"
  display_name         = "PagoPA/DEVOPS set advice 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.devops_set_advice.id
  management_group_id  = data.azurerm_management_group.devops_sl_pagamenti_servizi.id

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
          "value": ${local.list_allow_skus_raw_devops}
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}
