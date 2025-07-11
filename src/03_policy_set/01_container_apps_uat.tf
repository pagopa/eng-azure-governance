locals {
  container_apps_uat = {
    min_execution = {
      reference_id = "min_execution_reference_id"
      effect       = "Audit"
    }
  }
}

resource "azurerm_policy_set_definition" "container_apps_uat" {
  name                = "container_apps_uat"
  policy_type         = "Custom"
  display_name        = "PagoPA Container Apps UAT"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_uat"
    version  = "v1.0.0"
    ASC      = "true"
    parameterScopes = {
      for _, param in local.container_apps_uat : "${param.reference_id} : ${param.reference_id}" => data.azurerm_management_group.pagopa.id
    }
  })

  # Container Apps Jobs must have min execution equal to 0
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_container_apps.outputs.min_execution_id
    reference_id         = local.container_apps_uat.min_execution.reference_id
    parameter_values = jsonencode({
      effect = {
        value = local.container_apps_uat.min_execution.effect
      }
    })
  }
}

output "container_apps_uat_id" {
  value = azurerm_policy_set_definition.container_apps_uat.id
}
