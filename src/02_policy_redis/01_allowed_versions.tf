resource "azurerm_policy_definition" "redis_allowed_versions" {
  name                = "redis_allowed_versions"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Redis allowed versions"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use Redis allowed versions"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_versions_parameters.json")

  policy_rule = file("./policy_rules/allowed_versions_policy.json")

}
