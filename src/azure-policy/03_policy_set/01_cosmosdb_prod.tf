resource "azurerm_policy_set_definition" "cosmosdb_prod" {
  name                = "cosmosdb_prod"
  policy_type         = "Custom"
  display_name        = "PagoPA CosmosDB PROD"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_prod"
    version  = "v1.0.0"
    ASC      = "true"
  })

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["cosmosdb_required_network"].id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["cosmosdb_allowed_tls"].id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["cosmosdb_required_backup_policy"].id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["cosmosdb_required_primary_zone_redundancy"].id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["cosmosdb_forbidden_secondary_zone_redundancy"].id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["cosmosdb_dynamic_scaling_enabled"].id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["cosmosdb_automatic_failover_enabled"].id
    parameter_values     = jsonencode({})
  }

  policy_definition_reference {
    policy_definition_id = data.azurerm_policy_definition.this["cosmosdb_allowed_capacity_mode"].id
    parameter_values     = jsonencode({})
  }

}

output "cosmosdb_prod_id" {
  value = azurerm_policy_set_definition.cosmosdb_prod.id
}
