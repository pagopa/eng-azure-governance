resource "azurerm_policy_definition" "api_management_require_vnet" {
  name                = "api_management_require_vnet"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA API Management require vnet"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Integrate API Management in a VNet",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/require_vnet_parameters.json")

  policy_rule = file("./policy_rules/require_vnet_policy.json")
}
