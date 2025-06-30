# Add Custom Policy for tls 1.2 and 1.3
resource "azurerm_policy_definition" "app_service_apps_tls_custom" {
  name         = "app-service-apps-allow-tls-1-2-and-1-3"
  policy_type  = "Custom"
  mode         = "Indexed"
  display_name = "App Service Apps should use TLS 1.2 or 1.3"
  description  = "Ensures App Service Apps use TLS 1.2 or 1.3"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use App Service Apps allowed TLS"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_app_service_apps_tlsversion_parameters.json")
  policy_rule = file("./policy_rules/allowed_app_service_apps_tlsversion_policy.json")

}