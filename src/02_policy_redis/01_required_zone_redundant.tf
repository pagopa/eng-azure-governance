resource "azurerm_policy_definition" "redis_required_zone_redundant" {
  name                = "redis_required_zone_redundant"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Redis required zone redundant"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use Redis required zone redundant"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/required_zone_redundant_parameters.json")

  policy_rule = file("./policy_rules/required_zone_redundant_policy.json")

}
