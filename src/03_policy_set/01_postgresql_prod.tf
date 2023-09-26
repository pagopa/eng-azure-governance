locals {
  postgresql_prod = {
    metadata_category_name = "pagopa_prod"
  }
}

resource "azurerm_policy_set_definition" "postgresql_prod" {
  name                = "postgresql_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA Database for PostgreSQL PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
     {
         "category": "${local.postgresql_prod.metadata_category_name}",
         "version": "v1.0.0",
         "ASC": "true"
     }
 METADATA

  # Geo-redundant backup should be enabled for Azure Database for PostgreSQL
  policy_definition_reference {
    policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/48af4db5-9b8b-401c-8e74-076be876a430"
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_postgresql.outputs.postgres_required_flexible_georedundancy_id
  }
}

output "postgresql_prod_id" {
  value = azurerm_policy_set_definition.postgresql_prod.id
}
