variable "postgresql_prod" {
  type = object({
    listofallowedflexibleskuname = list(string)
    listofallowedskuname         = list(string)
  })
  default = {
    listofallowedflexibleskuname = [
      "Standard_D2ds_v4",
      "Standard_D4ds_v4",
      "Standard_D8ds_v4",
      "Standard_D2ds_v5",
      "Standard_D4ds_v5",
      "Standard_D8ds_v5",
    ]
    listofallowedskuname = [
      "GP_Gen5_2",
      "GP_Gen5_4",
      "GP_Gen5_8",
    ]
  }
  description = "List of PostgreSQL policy set parameters"
}

resource "azurerm_policy_set_definition" "postgresql_prod" {
  name                = "postgresql_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Database for PostgreSQL PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
     {
         "category": "pagopa_prod",
         "version": "v1.0.0",
         "ASC": "true"
     }
  METADATA

  # Geo-redundant backup should be enabled for Azure Database for PostgreSQL
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/48af4db5-9b8b-401c-8e74-076be876a430"
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgresql_required_flexible_georedundancy_id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgresql_allowed_flexible_sku_id
    reference_id         = local.postgresql.listofallowedflexiblesku
    parameter_values     = <<VALUE
    {
      "listOfAllowedSKU": {
        "value": ${jsonencode(var.postgresql_prod.listofallowedflexibleskuname)}
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgresql_allowed_sku_id
    reference_id         = local.postgresql.listofallowedsku
    parameter_values     = <<VALUE
    {
      "listOfAllowedSKU": {
        "value": ${jsonencode(var.postgresql_prod.listofallowedskuname)}
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgresql_required_engine_version_id
    parameter_values     = jsonencode({})
  }
}

output "postgresql_prod_id" {
  value = azurerm_policy_set_definition.postgresql_prod.id
}
