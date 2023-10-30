locals {
  network_prod = {
    metadata_category_name = "pagopa_prod"
    deny_zonal_publicip = {
      effect = "Audit"
    }
  }
}

resource "azurerm_policy_set_definition" "network_prod" {
  name                = "network_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Network PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.network_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true",
        "parameterScopes": {}
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_network.outputs.network_deny_zonal_publicip_id
    parameter_values = jsonencode({
      "effect" : {
        "value" : local.network_prod.deny_zonal_publicip.effect
      }
    })
  }
}

output "network_prod_id" {
  value = azurerm_policy_set_definition.network_prod.id
}
