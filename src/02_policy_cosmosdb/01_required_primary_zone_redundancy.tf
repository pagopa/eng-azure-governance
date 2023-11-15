resource "azurerm_policy_definition" "cosmosdb_required_primary_zone_redundancy" {
  name                = "cosmosdb_required_primary_zone_redundancy"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA CosmosDB required zone redundancy for primary region"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Enable zone redundancy for primary region"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/required_primary_zone_redundancy_parameters.json")

  policy_rule = file("./policy_rules/required_primary_zone_redundancy_policy.json")
}
