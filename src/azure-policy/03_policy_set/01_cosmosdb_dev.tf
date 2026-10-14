resource "azurerm_policy_set_definition" "cosmosdb_dev" {
  name                = "cosmosdb_dev"
  policy_type         = "Custom"
  display_name        = "PagoPA CosmosDB DEV"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_dev"
    version  = "v1.0.0"
    ASC      = "true"
  })

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_cosmosdb.outputs.cosmosdb_dynamic_scaling_enabled_id
    parameter_values     = jsonencode({})
  }

}

output "cosmosdb_dev_id" {
  value = azurerm_policy_set_definition.cosmosdb_dev.id
}
