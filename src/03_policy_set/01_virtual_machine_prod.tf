locals {
  virtual_machine_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "virtual_machine_prod" {
  name                = "virtual_machine_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA virtual_machine PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.virtual_machine_prod.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_virtual_machine.outputs.virtual_machine_allowed_sku_id
  }
}

output "virtual_machine_prod_id" {
  value = azurerm_policy_set_definition.virtual_machine_prod.id
}
