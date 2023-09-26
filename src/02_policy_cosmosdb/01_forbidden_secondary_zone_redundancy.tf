resource "azurerm_policy_definition" "cosmosdb_forbidden_secondary_zone_redundancy" {
  name                = "cosmosdb_forbidden_secondary_zone_redundancy"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA CosmosDB forbidden zone redundancy for primary region"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Disable zone redundancy for secondary region",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/forbidden_secondary_zone_redundancy_parameters.json")

  policy_rule = file("./policy_rules/forbidden_secondary_zone_redundancy_policy.json")

}
