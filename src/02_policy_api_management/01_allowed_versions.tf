resource "azurerm_policy_definition" "api_management_allowed_versions" {
  name                = "api_management_allowed_versions"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA API Management allowed versions"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use allowed API Management versions"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_versions_parameters.json")

  policy_rule = file("./policy_rules/allowed_versions_policy.json")
}
