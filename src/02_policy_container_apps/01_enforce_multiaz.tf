resource "azurerm_policy_definition" "enforce_multiaz" {
  name                = "enforce_multiaz"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Container Apps enforce multi-az"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Use multi-az for container apps",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/enforce_multiaz_parameters.json")

  policy_rule = file("./policy_rules/enforce_multiaz_policy.json")

}
