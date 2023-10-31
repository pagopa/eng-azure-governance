locals {
  postgresql_uat = {
    metadata_category_name = "pagopa_uat"
  }
}

variable "postgresql_uat" {
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
      "GP_Gen5_2",
    ]
  }
  description = "List of PostgreSQL policy set parameters"
}

resource "azurerm_policy_set_definition" "postgresql_uat" {
  name                = "postgresql_uat"
  policy_type         = "Custom"
  display_name        = "PagoPA Database for PostgreSQL UAT"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
     {
         "category": "${local.postgresql_uat.metadata_category_name}",
         "version": "v1.0.0",
         "ASC": "true"
     }
  METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgresql_allowed_flexible_sku_id
    reference_id         = local.postgresql.listofallowedflexiblesku
    parameter_values     = <<VALUE
    {
      "listOfAllowedSKU": {
        "value": ${jsonencode(var.postgresql_uat.listofallowedflexibleskuname)}
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
        "value": ${jsonencode(var.postgresql_uat.listofallowedskuname)}
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgresql_required_engine_version_id
    parameter_values     = jsonencode({})
  }
}

output "postgresql_uat_id" {
  value = azurerm_policy_set_definition.postgresql_uat.id
}
