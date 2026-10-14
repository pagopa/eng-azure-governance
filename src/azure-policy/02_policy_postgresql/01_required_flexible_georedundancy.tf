resource "azurerm_policy_definition" "postgresql_required_flexible_georedundancy" {
  name                = "postgresql_required_flexible_georedundancy"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Database for PostgreSQL Flexible required georedundancy"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Enable georedundancy for PostgreSQL flexible"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/required_flexible_georedundancy_parameters.json")

  policy_rule = file("./policy_rules/required_flexible_georedundancy_policy.json")
}
