resource "azurerm_policy_definition" "cosmosdb_allowed_capacity_mode" {
  name                = "cosmosdb_allowed_capacity_mode"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA CosmosDB allowed capacity mode"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Change capabilities for CosmosDB"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_capacity_mode_parameters.json")

  policy_rule = file("./policy_rules/allowed_capacity_mode_policy.json")

}
