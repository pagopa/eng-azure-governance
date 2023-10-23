resource "azurerm_policy_set_definition" "tags" {
  name                = "tags"
  policy_type         = "Custom"
  display_name        = "PagoPA Tags"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "pagopa_prod",
        "version": "v1.0.0",
        "ASC": "true"
    }
METADATA

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_tags.outputs.tags_require_tag_id
    parameter_values     = <<VALUE
    {
      "tagName": {
        "value": "Owner"
      }
    }
    VALUE
  }

  policy_definition_reference {
    policy_definition_id = data.terraform_remote_state.policy_tags.outputs.tags_require_tag_id
    parameter_values     = <<VALUE
    {
      "tagName": {
        "value": "Environment"
      }
    }
    VALUE
  }
}
