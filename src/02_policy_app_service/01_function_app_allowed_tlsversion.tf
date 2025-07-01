# Add Custom Policy for tls 1.2 and 1.3
resource "azurerm_policy_definition" "function_app_allowed_tls" {
  name                = "function_app_allowed_tls"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Function App allowed TLS versions"
  description         = "Ensures Function Apps use allowed TLS versions"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use App Service Function allowed TLS"
      Severity               = "High"
    }
  })

  parameters  = file("./policy_rules/allowed_function_app_tlsversion_parameters.json")
  policy_rule = file("./policy_rules/allowed_function_app_tlsversion_policy.json")

}