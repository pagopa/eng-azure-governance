resource "azurerm_policy_definition" "cosmosdb_forbidden_capabilities" {
  name                = "cosmosdb_forbidden_capabilities"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA CosmosDB forbidden capabilities"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Change capabilities for CosmosDB"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/forbidden_capabilities_parameters.json")

  policy_rule = file("./policy_rules/forbidden_capabilities_policy.json")

}
