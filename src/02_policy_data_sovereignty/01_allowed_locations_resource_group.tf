resource "azurerm_policy_definition" "allowed_locations_resource_group" {
  name                = "allowed_locations_resource_group"
  policy_type         = "Custom"
  mode                = "All"
  display_name        = "PagoPA Allowed locations for resource groups"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
    securityCenter = {
      RemediationDescription = "Use allowed locations for resource groups"
      Severity               = "High"
    }
  })

  parameters = file("./policy_rules/allowed_locations_resource_groups_parameters.json")

  policy_rule = file("./policy_rules/allowed_locations_resource_groups_policy.json")

}
