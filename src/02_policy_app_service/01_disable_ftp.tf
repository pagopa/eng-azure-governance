resource "azurerm_policy_definition" "app_service_disable_ftp" {
  name                = "app_service_disable_ftp"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA App Service disable FTP and FTPS"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Disable App Service FTP and FTPS"
      Severity = "High"
    }
  })

  parameters = file("./policy_rules/disable_ftp_parameters.json")

  policy_rule = file("./policy_rules/disable_ftp_policy.json")
}
