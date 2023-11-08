locals {
  api_management_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

variable "api_management_prod" {
  type = object({
    listofallowedskusname = list(string)
  })
  default = {
    listofallowedskusname = ["Premium"]
  }
  description = "List of API Management policy set parameters"
}

resource "azurerm_policy_set_definition" "api_management_prod" {
  name                = "api_management_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA API Management PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.api_management_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  # API Management service should use a SKU that supports virtual networks
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/73ef9241-5d81-4cd4-b483-8443d1730fe5"
    reference_id         = local.api_management.listofallowedskus
    parameter_values     = <<VALUE
    {
      "listOfAllowedSKUs": {
        "value": ${jsonencode(var.api_management_prod.listofallowedskusname)}
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_api_management.outputs.api_management_allowed_versions_id
    parameter_values     = jsonencode({})
  }

  # Require Internal VPN
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/eb969283-cfab-4a68-a8a8-2b1fdd5feef8"
    parameter_values     = jsonencode({})
  }
}

output "api_management_prod_id" {
  value = azurerm_policy_set_definition.api_management_prod.id
}
