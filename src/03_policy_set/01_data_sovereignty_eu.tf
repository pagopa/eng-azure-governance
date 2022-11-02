variable "allowed_locations" {
  type        = list(string)
  default     = ["northeurope", "westeurope", "global"]
  description = "description"
}

variable "allowed_locations_resource_groups" {
  type        = list(string)
  default     = ["northeurope", "westeurope"]
  description = "description"
}

locals {
  data_sovereignty_eu = {
    allowed_locations_policy_definition_reference_id                 = "Allowed locations"
    allowed_locations_resource_groups_policy_definition_reference_id = "Allowed locations for resource groups"
  }
}

resource "azurerm_policy_set_definition" "data_sovereignty_eu" {
  name                = "data_sovereignty_eu"
  policy_type         = var.policy_type
  display_name        = "PagoPA Data sovereignty in EU"
  management_group_id = data.azurerm_management_group.root_pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "parameterScopes": {
          "listOfAllowedLocations : ${local.data_sovereignty_eu.allowed_locations_policy_definition_reference_id}": "${data.azurerm_management_group.root_pagopa.id}",
          "listOfAllowedLocations : ${local.data_sovereignty_eu.allowed_locations_resource_groups_policy_definition_reference_id}": "${data.azurerm_management_group.root_pagopa.id}"
        }
    }
METADATA

  # Allowed locations
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/e56962a6-4747-49cd-b67b-bf8b01975c4c"
    reference_id         = local.data_sovereignty_eu.allowed_locations_policy_definition_reference_id
    parameter_values     = <<VALUE
    {
      "listOfAllowedLocations": {
        "value": ${jsonencode(var.allowed_locations)}
      }
    }
    VALUE
  }

  # Allowed locations for resource groups
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/e765b5de-1225-4ba3-bd56-1ac6695af988"
    reference_id         = local.data_sovereignty_eu.allowed_locations_resource_groups_policy_definition_reference_id
    parameter_values     = <<VALUE
    {
      "listOfAllowedLocations": {
        "value": ${jsonencode(var.allowed_locations_resource_groups)}
      }
    }
    VALUE
  }
}
