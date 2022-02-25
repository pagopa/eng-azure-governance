#
# Enforced
#
resource "azurerm_policy_set_definition" "prod_set_enforced" {
  name                  = "pagopa_prod_set_enforced"
  policy_type           = "Custom"
  display_name          = "PagoPA policy enforced set/initiatives for prod management group"
  management_group_name = data.azurerm_management_group.prod_sl_pagamenti_servizi.name

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

#
# Advices
#
resource "azurerm_policy_set_definition" "prod_set_advice" {
  name                  = "pagopa_prod_set_advice"
  policy_type           = "Custom"
  display_name          = "PagoPA policy advice set/initiatives for prod management group"
  management_group_name = data.azurerm_management_group.prod_sl_pagamenti_servizi.name

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
