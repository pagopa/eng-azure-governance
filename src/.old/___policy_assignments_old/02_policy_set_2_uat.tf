# Enforced
resource "azurerm_policy_set_definition" "uat_set_enforced" {
  name                = "pagopa_uat_set_enforced"
  policy_type         = "Custom"
  display_name        = "PagoPA policy enforced set/initiatives for uat management group"
  management_group_id = data.azurerm_management_group.uat_sl_pagamenti_servizi.id

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

  # Allowed locations for resource groups
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/e765b5de-1225-4ba3-bd56-1ac6695af988"
    parameter_values     = <<VALUE
    {
      "listOfAllowedLocations": {
        "value": "[parameters('listOfAllowedLocations')]"
      }
    }
    VALUE
  }
}

# Advice
resource "azurerm_policy_set_definition" "uat_set_advice" {
  name                = "pagopa_uat_set_advice"
  policy_type         = "Custom"
  display_name        = "PagoPA policy advice set/initiatives for uat management group"
  management_group_id = data.azurerm_management_group.uat_sl_pagamenti_servizi.id

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

  # allowed skus
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
  list_allowed_locations_uat = jsonencode(var.uat_allowed_locations)
  list_allow_skus_raw_uat    = jsonencode(var.uat_vm_skus_allowed)
}

#
# Enforced
#
resource "azurerm_management_group_policy_assignment" "uat_set_enforced_2_root_sl_pay" {
  name                 = "pa_uatsetenf2rootslpay"
  display_name         = "PagoPA/DEVOPS/UAT/SET/ENFORCED 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.uat_set_enforced.id
  management_group_id  = data.azurerm_management_group.uat_sl_pagamenti_servizi.id

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
          "value": ${local.list_allowed_locations_uat}
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
resource "azurerm_management_group_policy_assignment" "uat_set_advice_2_root_sl_pay" {
  name                 = "pa_uatsetadv2rootslpay"
  display_name         = "PagoPA/UAT/SET/ADVICE 2 Mgmt root sl servizi e pagamenti"
  policy_definition_id = azurerm_policy_set_definition.uat_set_advice.id
  management_group_id  = data.azurerm_management_group.uat_sl_pagamenti_servizi.id

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
          "value": ${local.list_allow_skus_raw_uat}
      }
  }
PARAMS

  identity {
    type = "SystemAssigned"
  }
}
