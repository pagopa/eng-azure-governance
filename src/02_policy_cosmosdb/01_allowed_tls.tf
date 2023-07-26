resource "azurerm_policy_definition" "cosmosdb_allowed_tls" {
  name                = "cosmosdb_allowed_tls"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA CosmosDB allowed tls"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Use CosmosDB allowed tls",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/allowed_tls_parameters.json")

  policy_rule = file("./policy_rules/allowed_tls_policy.json")

}
