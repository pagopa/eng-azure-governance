locals {
  virtual_machine_scale_set_dev = {
    metadata_category_name = "pagopa_dev"
  }
}

variable "virtual_machine_scale_set_dev" {
  type = object({
    listofallowedskuname = list(string)
  })
  default = {
    listofallowedskuname = [
      "Standard_B2ms",
      "Standard_B4ms",
      "Standard_B8ms",
    ]
  }
  description = "List of Virtual Machine policy set parameters"
}

resource "azurerm_policy_set_definition" "virtual_machine_scale_set_dev" {
  name                = "virtual_machine_scale_set_dev"
  policy_type         = "Custom"
  display_name        = "PagoPA Virtual Machine Scale Set DEV"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${local.virtual_machine_scale_set_dev.metadata_category_name}",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_virtual_machine_scale_set.outputs.virtual_machine_scale_set_allowed_sku_id
    reference_id         = local.virtual_machine_scale_set.listofallowedsku
    parameter_values     = <<VALUE
    {
      "listOfAllowedSKU": {
        "value": ${jsonencode(var.virtual_machine_scale_set_dev.listofallowedskuname)}
      }
    }
    VALUE
  }
}

output "virtual_machine_scale_set_dev_id" {
  value = azurerm_policy_set_definition.virtual_machine_scale_set_dev.id
}