variable "virtual_machine_uat" {
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

resource "azurerm_policy_set_definition" "virtual_machine_uat" {
  name                = "virtual_machine_uat"
  policy_type         = "Custom"
  display_name        = "PagoPA Virtual Machine UAT"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "pagopa_uat",
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
        "value": ${jsonencode(var.virtual_machine_uat.listofallowedskuname)}
      }
    }
    VALUE
  }
}

output "virtual_machine_uat_id" {
  value = azurerm_policy_set_definition.virtual_machine_uat.id
}
