locals {
  api_management_uat = {
    metadata_category_name = "pagopa_uat"
  }
}

variable "api_management_uat" {
  type = object({
    listofallowedskusname = list(string)
  })
  default = {
    listofallowedskusname = ["Developer"]
  }
  description = "List of API Management policy set parameters"
}

resource "azurerm_policy_set_definition" "api_management_uat" {
  name                = "api_management_uat"
  policy_type         = "Custom"
  display_name        = "PagoPA API Management UAT"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.api_management_uat.metadata_category_name}",
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
        "value": ${jsonencode(var.api_management_uat.listofallowedskusname)}
      }
    }
    VALUE
  }
}

output "api_management_uat_id" {
  value = azurerm_policy_set_definition.api_management_uat.id
}
