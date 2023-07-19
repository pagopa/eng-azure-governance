locals {
  app_service_dev = {
    metadata_category_name = "pagopa_dev"
  }
}

variable "app_service_dev" {
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

resource "azurerm_policy_set_definition" "app_service_dev" {
  name                = "app_service_dev"
  policy_type         = "Custom"
  display_name        = "PagoPA App Service DEV"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.app_service_dev.metadata_category_name}",
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
        "value": ${jsonencode(var.app_service_dev.listofallowedsku)}
      },
      "listOfAllowedKind": {
        "value": ${jsonencode(var.app_service_dev.listofallowedkind)}
      }
    }
    VALUE
  }
}

output "app_service_dev_id" {
  value = azurerm_policy_set_definition.app_service_dev.id
}
