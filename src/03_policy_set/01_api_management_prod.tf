locals {
  api_management_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "api_management_prod" {
  name                = "api_management_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA API Management PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.api_management_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_api_management.outputs.api_management_allowed_sku_id
  }
}

output "api_management_prod_id" {
  value = azurerm_policy_set_definition.api_management_prod.id
}
