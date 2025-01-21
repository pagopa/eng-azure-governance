resource "azurerm_policy_definition" "cosmosdb_dynamic_scaling_enabled" {
  name                = "cosmosdb_dynamic_scaling_enabled"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA CosmosDB must have dynamic scaling enabled"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Enable Dynamic Scaling for CosmosDB"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/dynamic_scaling_enabled_parameters.json")

  policy_rule = file("./policy_rules/dynamic_scaling_enabled_policy.json")

}
