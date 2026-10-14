resource "azurerm_policy_definition" "require_tag_values" {
  name                = "require_tag_values"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA require tag values"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })

  parameters = file("./policy_rules/require_tag_values_parameters.json")

  policy_rule = file("./policy_rules/require_tag_values_policy.json")
}
