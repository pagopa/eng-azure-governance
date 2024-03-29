resource "azurerm_policy_definition" "app_service_allowed_linuxfxversion" {
  name                = "app_service_allowed_linuxfxversion"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA App Service allowed linuxfxversion"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use App Service allowed linuxfxversion"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_app_service_linuxfxversion_parameters.json")

  policy_rule = file("./policy_rules/allowed_app_service_linuxfxversion_policy.json")

}

