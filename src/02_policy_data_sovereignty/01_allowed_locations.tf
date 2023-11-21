resource "azurerm_policy_definition" "allowed_locations" {
  name                = "allowed_locations"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Allowed locations"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use allowed locations"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_locations_parameters.json")

  policy_rule = file("./policy_rules/allowed_locations_policy.json")

}
