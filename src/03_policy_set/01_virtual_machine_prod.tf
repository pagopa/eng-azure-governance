locals {
  virtual_machine_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

variable "virtual_machine_prod" {
  type = object({
    listofallowedskuname = list(string)
  })
  default = {
    listofallowedskuname = [
      "Standard_D2ds_v5",
      "Standard_D4ds_v5",
      "Standard_D8ds_v5",
    ]
  }
  description = "List of Virtual Machine policy set parameters"
}

resource "azurerm_policy_set_definition" "virtual_machine_prod" {
  name                = "virtual_machine_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Virtual Machine PROD"
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
    reference_id         = local.virtual_machine.listofallowedsku
    parameter_values     = <<VALUE
    {
      "listOfAllowedSKU": {
        "value": ${jsonencode(var.virtual_machine_prod.listofallowedskuname)}
      }
    }
    VALUE
  }
}

output "virtual_machine_prod_id" {
  value = azurerm_policy_set_definition.virtual_machine_prod.id
}
