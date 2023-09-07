locals {
  api_management_uat = {
    metadata_category_name = "pagopa_uat"
  }
}

resource "azurerm_policy_set_definition" "api_management_uat" {
  name                = "api_management_uat"
  policy_type         = "Custom"
  display_name        = "PagoPA API Management uat"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.api_management_uat.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_api_management.outputs.api_management_allowed_sku_id
  }
}

output "api_management_uat_id" {
  value = azurerm_policy_set_definition.api_management_uat.id
}
