variable "postgresql_dev" {
  type = object({
    listofallowedskuname         = list(string)
    listofallowedflexibleskuname = list(string)
  })
  default = {
    listofallowedflexibleskuname = [
      "Standard_B1ms",
      "Standard_B2s",
      "Standard_B2ms",
      # "Standard_B4ms",
      # "Standard_B8ms",
    ]
    listofallowedskuname = [
      "B_Gen5_1",
      "B_Gen5_2",
      "GP_Gen5_2",
    ]
  }
  description = "List of PostgreSQL policy set parameters"
}

resource "azurerm_policy_set_definition" "postgresql_dev" {
  name                = "postgresql_dev"
  policy_type         = "Custom"
  display_name        = "PagoPA Database for PostgreSQL DEV"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_dev"
    version  = "v1.0.0"
    ASC      = "true"
  })

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgresql_allowed_flexible_sku_id
    reference_id         = local.postgresql.listofallowedflexiblesku
    parameter_values = jsonencode({
      listOfAllowedSKU = {
        value = var.postgresql_dev.listofallowedflexibleskuname
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgresql_allowed_sku_id
    reference_id         = local.postgresql.listofallowedsku
    parameter_values = jsonencode({
      listOfAllowedSKU = {
        value = var.postgresql_dev.listofallowedskuname
      }
    })
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgresql_required_engine_version_id
    parameter_values     = jsonencode({})
  }
}

output "postgresql_dev_id" {
  value = azurerm_policy_set_definition.postgresql_dev.id
}
