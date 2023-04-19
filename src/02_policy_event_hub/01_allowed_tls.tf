resource "azurerm_policy_definition" "eventhub_allowed_tls" {
  name                = "eventhub_allowed_tls"
  policy_type         = "Custom"
  mode                = "All"
  display_name        = "PagoPA EventHub allowed tls"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Use EventHub allowed tls",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/allowed_tls_parameters.json")

  policy_rule = file("./policy_rules/allowed_tls_policy.json")

}
