resource "azurerm_policy_definition" "require_tag" {
  name                = "require_tag"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA require tag"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  parameters = file("./policy_rules/require_tag_parameters.json")

  policy_rule = file("./policy_rules/require_tag_policy.json")
}
