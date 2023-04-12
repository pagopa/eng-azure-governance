resource "azurerm_policy_definition" "eventhub_required_network" {
  name                = "eventhub_required_network"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA EventHub required network restrictions"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Use EventHub required network restrictions",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/required_network_parameters.json")

  policy_rule = file("./policy_rules/required_network_policy.json")

}
