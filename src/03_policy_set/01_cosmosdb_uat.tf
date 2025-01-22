resource "azurerm_policy_set_definition" "cosmosdb_uat" {
  name                = "cosmosdb_uat"
  policy_type         = "Custom"
  display_name        = "PagoPA CosmosDB UAT"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = "pagopa_uat"
    version  = "v1.0.0"
    ASC      = "true"
  })

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_cosmosdb.outputs.cosmosdb_dynamic_scaling_enabled_id
    parameter_values     = jsonencode({})
  }

}

output "cosmosdb_uat_id" {
  value = azurerm_policy_set_definition.cosmosdb_uat.id
}
