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
    metadata_category_name                                           = "pagopa_global"
    allowed_locations_policy_definition_reference_id                 = "Allowed locations"
    allowed_locations_resource_groups_policy_definition_reference_id = "Allowed locations for resource groups"
  }
}

resource "azurerm_policy_set_definition" "data_sovereignty_eu" {
  name                = "data_sovereignty_eu"
  policy_type         = "Custom"
  display_name        = "PagoPA Data sovereignty in EU"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.data_sovereignty_eu.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true",
        "parameterScopes": {
          "listOfAllowedLocations : ${local.data_sovereignty_eu.allowed_locations_policy_definition_reference_id}": "${data.azurerm_management_group.pagopa.id}",
          "listOfAllowedLocations : ${local.data_sovereignty_eu.allowed_locations_resource_groups_policy_definition_reference_id}": "${data.azurerm_management_group.pagopa.id}"
        }
    }
METADATA

  # Allowed locations
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_redis.outputs.allowed_locations_id
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
    policy_definition_id = data.terraform_remote_state.policy_redis.outputs.allowed_locations_resource_group_id
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

output "data_sovereignty_eu_id" {
  value = azurerm_policy_set_definition.data_sovereignty_eu.id
}
