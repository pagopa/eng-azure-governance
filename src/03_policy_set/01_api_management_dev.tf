variable "api_management_dev" {
  type = object({
    listofallowedskusname = list(string)
  })
  default = {
    listofallowedskusname = ["Developer"]
  }
  description = "List of API Management policy set parameters"
}

resource "azurerm_policy_set_definition" "api_management_dev" {
  name                = "api_management_dev"
  policy_type         = "Custom"
  display_name        = "PagoPA API Management DEV"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_dev"
    version  = "v1.0.0"
    ASC      = "true"
  })

  # API Management service should use a SKU that supports virtual networks
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/73ef9241-5d81-4cd4-b483-8443d1730fe5"
    reference_id         = local.api_management.listofallowedskus
    parameter_values = jsonencode({
      listOfAllowedSKUs = {
        value = var.api_management_dev.listofallowedskusname
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_api_management.outputs.api_management_allowed_versions_id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_api_management.outputs.api_management_require_vnet_id
    parameter_values     = jsonencode({})
  }
}

output "api_management_dev_id" {
  value = azurerm_policy_set_definition.api_management_dev.id
}
