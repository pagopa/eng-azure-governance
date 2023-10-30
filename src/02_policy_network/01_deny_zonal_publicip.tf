resource "azurerm_policy_definition" "network_deny_zonal_publicip" {
  name                = "network_deny_zonal_publicip"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA network deny zonal Public IP"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Use zone redundancy for Public IP",
		      "Severity": "High"
        }
    }
METADATA

  parameters = file("./policy_rules/deny_zonal_publicip_parameters.json")

  policy_rule = file("./policy_rules/deny_zonal_publicip_policy.json")

}
