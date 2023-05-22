locals {
  app_service_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "app_service_prod" {
  name                = "app_service_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA App Service PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.app_service_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_app_service.outputs.app_service_allowed_linuxfxversion_id
  }

}

output "app_service_prod_id" {
  value = azurerm_policy_set_definition.app_service_prod.id
}
