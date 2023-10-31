locals {
  container_apps_prod = {
    metadata_category_name = "pagopa_prod"
    enforce_multiaz = {
      reference_id = "enforce_multiaz_reference_id"
      effect       = "Audit"
    }
  }
}

resource "azurerm_policy_set_definition" "container_apps_prod" {
  name                = "container_apps_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Container Apps PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.container_apps_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true",
        "parameterScopes": {
          "${local.container_apps_prod.enforce_multiaz.reference_id} : ${local.container_apps_prod.enforce_multiaz.reference_id}": "${data.azurerm_management_group.pagopa.id}"
        }
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_container_apps.outputs.enforce_multiaz_id
    reference_id         = local.container_apps_prod.enforce_multiaz.reference_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.container_apps_prod.enforce_multiaz.effect
      }
    })
  }
}

output "container_apps_prod_id" {
  value = azurerm_policy_set_definition.container_apps_prod.id
}
