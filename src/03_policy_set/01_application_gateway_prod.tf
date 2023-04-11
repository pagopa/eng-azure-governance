locals {
  application_gateway_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "application_gateway_prod" {
  name                = "application_gateway_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Storage Account PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.application_gateway_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_application_gateway.outputs.application_gateway_allowed_sku_id
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_application_gateway.outputs.application_gateway_allowed_ciphersuites_id
  }

}

output "application_gateway_prod_id" {
  value = azurerm_policy_set_definition.application_gateway_prod.id
}
