resource "azurerm_policy_definition" "application_gateway_allowed_ciphersuites" {
  name                = "application_gateway_allowed_ciphersuites"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Application Gateway allowed Cipher Suites"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use Application Gateway allowed Cipher Suites"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_ciphersuites_parameters.json")

  policy_rule = file("./policy_rules/allowed_ciphersuites_policy.json")

}
