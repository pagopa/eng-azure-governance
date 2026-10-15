locals {
  container_apps_prod = {
    enforce_multiaz = {
      reference_id = "enforce_multiaz_reference_id"
      effect       = "Audit"
    }
    enforce_private_subnets = {
      reference_id = "enforce_private_subnets_reference_id"
      effect       = "Audit"
    }
    min_execution = {
      reference_id = "min_execution_reference_id"
      effect       = "Audit"
    }
  }
}

resource "azurerm_policy_set_definition" "container_apps_prod" {
  name                = "container_apps_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Container Apps PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_prod"
    version  = "v1.0.0"
    ASC      = "true"
    parameterScopes = {
      for _, param in local.container_apps_prod : "${param.reference_id} : ${param.reference_id}" => data.azurerm_management_group.pagopa.id
    }
  })

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_container_apps.outputs.enforce_multiaz_id
    reference_id         = local.container_apps_prod.enforce_multiaz.reference_id
    parameter_values = jsonencode({
      effect = {
        value = local.container_apps_prod.enforce_multiaz.effect
      }
    })
  }

  # Container Apps environment should disable public network access
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/5e5dbe3f-2702-4ffc-8b1e-0cae008a5c71"
    reference_id         = local.container_apps_prod.enforce_private_subnets.reference_id
    parameter_values = jsonencode({
      effect = {
        value = local.container_apps_prod.enforce_private_subnets.effect
      }
    })
  }

  # Container Apps Jobs must have min execution equal to 0
  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_container_apps.outputs.min_execution_id
    reference_id         = local.container_apps_prod.min_execution.reference_id
    parameter_values = jsonencode({
      effect = {
        value = local.container_apps_prod.min_execution.effect
      }
    })
  }
}

output "container_apps_prod_id" {
  value = azurerm_policy_set_definition.container_apps_prod.id
}
