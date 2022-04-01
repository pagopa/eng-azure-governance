resource "azurerm_policy_set_definition" "devops_set_enforced" {
  name                = "pagopa_devops_set_enforced"
  policy_type         = "Custom"
  display_name        = "PagoPA policy set/initiatives enforced for devops management group"
  management_group_id = data.azurerm_management_group.devops_sl_pagamenti_servizi.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  parameters = <<PARAMETERS
  {
    "listOfAllowedLocations": {
      "type": "Array",
      "metadata": {
        "description": "The list of locations that can be specified when deploying resources.",
        "strongType": "location",
        "displayName": "Allowed locations"
      },
      "defaultValue" : [""]
    }
  }
PARAMETERS

  # Allowed Locations
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c"
    parameter_values     = <<VALUE
    {
      "listOfAllowedLocations": {
        "value": "[parameters('listOfAllowedLocations')]"
      }
    }
    VALUE
  }
}

resource "azurerm_policy_set_definition" "devops_set_advice" {
  name                = "pagopa_devops_set_advice"
  policy_type         = "Custom"
  display_name        = "PagoPA policy set/initiatives advice for devops management group"
  management_group_id = data.azurerm_management_group.devops_sl_pagamenti_servizi.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  parameters = <<PARAMETERS
  {
    "listOfAllowedSKUs": {
      "type": "Array",
      "metadata": {
        "description": "The list of size SKUs that can be specified for virtual machines.",
        "displayName": "Allowed Size SKUs",
        "strongType": "VMSKUs"
      },
      "defaultValue" : [""]
    }
  }
PARAMETERS

  # Allowed Skus
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/cccc23c7-8427-4f53-ad12-b6a63eb452b3"
    parameter_values     = <<VALUE
    {
      "listOfAllowedSKUs": {
        "value": "[parameters('listOfAllowedSKUs')]"
      }
    }
    VALUE
  }
}

#
# Asingment
#

locals {
  list_allowed_locations_devops = jsonencode(var.devops_allowed_locations)
  list_allow_skus_raw_devops    = jsonencode(var.devops_vm_skus_allowed)
}

resource "azurerm_management_group_policy_assignment" "devops_set_enforced_2_root_sl_pay" {
  name                 = "pa_dvopsenf2rootslpay"
  display_name         = "PagoPA/DEVOPS/SET/ADVICE 2 Mgmt root sl servizi e pagamenti"
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
  display_name         = "PagoPA/DEVOPS/SET/ADVICE 2 Mgmt root sl servizi e pagamenti"
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
