locals {
  api_management_dev = {
    metadata_category_name = "pagopa_dev"
  }
}

resource "azurerm_policy_set_definition" "api_management_dev" {
  name                = "api_management_dev"
  policy_type         = "Custom"
  display_name        = "PagoPA API Management dev"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.api_management_dev.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_api_management.outputs.api_management_allowed_sku_id
  }
}

output "api_management_dev_id" {
  value = azurerm_policy_set_definition.api_management_dev.id
}
