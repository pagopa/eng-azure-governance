resource "azurerm_policy_definition" "cosmosdb_required_network" {
  name                = "cosmosdb_required_network"
  policy_type         = "Custom"
  mode                = "All"
  display_name        = "PagoPA CosmosDB required network restrictions"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use CosmosDB required network restrictions"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/required_network_parameters.json")

  policy_rule = file("./policy_rules/required_network_policy.json")

}
