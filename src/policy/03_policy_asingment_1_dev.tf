locals {
  list_allowed_locations_dev = jsonencode(var.dev_allowed_locations)
  list_allow_skus_raw_dev    = jsonencode(var.dev_vm_skus_allowed)
}

#
# Enforce
#
resource "azurerm_management_group_policy_assignment" "dev_set_enforced_2_root_sl_pay" {
  name                 = "pa_devsetenf2rootslpay"
  display_name         = "PagoPA/Dev set Enforced 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.dev_set_enforced.id
  management_group_id  = data.azurerm_management_group.dev_sl_pagamenti_servizi.id

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
          "value": ${local.list_allowed_locations_dev}
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}

#
# Advice
#
resource "azurerm_management_group_policy_assignment" "dev_set_advice_2_root_sl_pay" {
  name                 = "pa_devsetadv2rootslpay"
  display_name         = "PagoPA/Dev set advice 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.dev_set_advice.id
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
      "listOfAllowedSKUs": {
          "value": ${local.list_allow_skus_raw_dev}
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}
