locals {
  app_service_uat = {
    metadata_category_name = "pagopa_uat"
  }
}

variable "app_service_uat" {
  type = object({
    listofallowedsku  = list(string)
    listofallowedkind = list(string)
  })
  default = {
    listofallowedsku  = ["Y1", "WS1", "B1", "B2", "B3"]
    listofallowedkind = ["elastic", "linux", "functionapp"]
  }
  description = "List of app service policy set parameters"
}

resource "azurerm_policy_set_definition" "app_service_uat" {
  name                = "app_service_uat"
  policy_type         = "Custom"
  display_name        = "PagoPA App Service UAT"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.app_service_uat.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true",
        "parameterScopes": {
          "${local.app_service.listofallowedsku} : ${local.app_service.listofallowedsku}": "${data.azurerm_management_group.pagopa.id}"
        }
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_app_service.outputs.app_service_allowed_linuxfxversion_id
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_app_service.outputs.function_app_allowed_linuxfxversion_id
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_app_service.outputs.app_service_allowed_sku_id
    reference_id         = local.app_service.listofallowedsku
    parameter_values     = <<VALUE
    {
      "listOfAllowedSku": {
        "value": ${jsonencode(var.app_service_uat.listofallowedsku)}
      },
      "listOfAllowedKind": {
        "value": ${jsonencode(var.app_service_uat.listofallowedkind)}
      }
    }
    VALUE
  }
}

output "app_service_uat_id" {
  value = azurerm_policy_set_definition.app_service_uat.id
}
