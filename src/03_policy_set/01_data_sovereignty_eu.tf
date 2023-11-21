variable "allowed_locations" {
  type        = list(string)
  default     = ["italynorth", "northeurope", "westeurope", "global"]
  description = "List of allowed locations for resources"
}

variable "allowed_locations_resource_groups" {
  type        = list(string)
  default     = ["italynorth", "northeurope", "westeurope"]
  description = "List of allowed locations for resource groups"
}

locals {
  data_sovereignty_eu = {
    allowed_locations_policy_definition = {
      reference_id = "allowed_locations_policy_definition_reference_id"
    }
    allowed_locations_resource_groups_policy_definition = {
      reference_id = "allowed_locations_resource_groups_policy_definition_reference_id"
    }
  }
}

resource "azurerm_policy_set_definition" "data_sovereignty_eu" {
  name                = "data_sovereignty_eu"
  policy_type         = "Custom"
  display_name        = "PagoPA Data sovereignty in EU"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_global"
    version  = "v1.0.0"
    ASC      = "true"
    parameterScopes = {
      for _, param in local.data_sovereignty_eu : "${param.reference_id} : ${param.reference_id}" => data.azurerm_management_group.pagopa.id
    }
  })

  # Allowed locations
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_data_sovereignty.outputs.allowed_locations_id
    reference_id         = local.data_sovereignty_eu.allowed_locations_policy_definition.reference_id
    parameter_values = jsonencode({
      listOfAllowedLocations = {
        value = var.allowed_locations
      }
    })
  }

  # Allowed locations for resource groups
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_data_sovereignty.outputs.allowed_locations_resource_group_id
    reference_id         = local.data_sovereignty_eu.allowed_locations_resource_groups_policy_definition.reference_id
    parameter_values = jsonencode({
      listOfAllowedLocations = {
        value = var.allowed_locations_resource_groups
      }
    })
  }
}

output "data_sovereignty_eu_id" {
  value = azurerm_policy_set_definition.data_sovereignty_eu.id
}
