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

  metadata = jsonencode({
    category = "pagopa_uat"
    version  = "v1.0.0"
    ASC      = "true"
    parameterScopes = {
      for _, param in local.app_service : "${param.reference_id} : ${param.reference_id}" => data.azurerm_management_group.pagopa.id
    }
  })

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_app_service.outputs.app_service_allowed_linuxfxversion_id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_app_service.outputs.function_app_allowed_linuxfxversion_id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_app_service.outputs.app_service_allowed_sku_id
    reference_id         = local.app_service.listofallowedsku.reference_id
    parameter_values = jsonencode({
      listOfAllowedSku = {
        value = var.app_service_uat.listofallowedsku
      }
      listOfAllowedKind = {
        value = var.app_service_uat.listofallowedkind
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_app_service.outputs.app_service_disable_ftp_id
    parameter_values     = jsonencode({})
  }

  # Function app slots should use the latest TLS version
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/deb528de-8f89-4101-881c-595899253102"
    parameter_values     = jsonencode({})
  }

  # Function apps should use the latest TLS version
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/f9d614c5-c173-4d56-95a7-b4437057d193"
    parameter_values     = jsonencode({})
  }

  # App Service apps should use the latest TLS version
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/f0e6e85b-9b9f-4a4b-b67b-f730d42f1b0b"
    parameter_values     = jsonencode({})
  }

  # App Service app slots should use the latest TLS version
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/4ee5b817-627a-435a-8932-116193268172"
    parameter_values     = jsonencode({})
  }

  # App Service app slots should only be accessible over HTTPS
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/ae1b9a8c-dfce-4605-bd91-69213b4a26fc"
    parameter_values     = jsonencode({})
  }

  # App Service apps should only be accessible over HTTPS
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/a4af4a39-4135-47fb-b175-47fbdf85311d"
    parameter_values     = jsonencode({})
  }

  # Function apps should only be accessible over HTTPS
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/6d555dd1-86f2-4f1c-8ed7-5abae7c6cbab"
    parameter_values     = jsonencode({})
  }

  # Function app slots should only be accessible over HTTPS
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/5e5dbe3f-2702-4ffc-8b1e-0cae008a5c71"
    parameter_values     = jsonencode({})
  }
}

output "app_service_uat_id" {
  value = azurerm_policy_set_definition.app_service_uat.id
}
