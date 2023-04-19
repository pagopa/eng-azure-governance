resource "azurerm_policy_definition" "eventhub_required_zone_redundant" {
  name                = "eventhub_required_zone_redundant"
  policy_type         = "Custom"
  mode                = "All"
  display_name        = "PagoPA EventHub required zone redundant"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Use EventHub required zone redundant",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/required_zone_redundant_parameters.json")

  policy_rule = file("./policy_rules/required_zone_redundant_policy.json")

}
