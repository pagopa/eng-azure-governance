# Add Custom Policy for tls 1.2 and 1.3
resource "azurerm_policy_definition" "function_apps_tls_custom" {
  name         = "function-apps-allow-tls-1-2-and-1-3"
  policy_type  = "Custom"
  mode         = "Indexed"
  display_name = "Function Apps should use TLS 1.2 or 1.3"
  description  = "Ensures Function Apps use TLS 1.2 or 1.3"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use App Service Function allowed TLS"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_app_service_function_tlsversion_parameters.json")
  policy_rule = file("./policy_rules/allowed_app_service_function_tlsversion_policy.json")

}