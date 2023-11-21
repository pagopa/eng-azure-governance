resource "azurerm_policy_definition" "application_gateway_required_zones" {
  name                = "application_gateway_required_zones"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Application Gateway required availability zones"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use Application Gateway required availability zones"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/required_zones_parameters.json")

  policy_rule = file("./policy_rules/required_zones_policy.json")

}
