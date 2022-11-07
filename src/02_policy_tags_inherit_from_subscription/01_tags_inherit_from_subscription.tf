variable "tags_inherit_from_subscription" {
  type        = list(string)
  description = "Tag that must be inherith from the subscription"
  default = [
    "CostCenter",
    "Environment",
    "Owner",
    "BusinessUnit",
  ]
}

resource "azurerm_policy_definition" "tags_inherit_from_subscription" {
  for_each = toset(var.tags_inherit_from_subscription)

  name                = "tag_${lower(each.key)}_inherit_from_subscription"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Tag ${each.key} inherith from subscription"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  parameters = <<PARAMETERS
    {
      "tagName": {
        "type": "String",
        "metadata": {
          "displayName": "Tag Name",
          "description": "Name of the tag, such as 'environment'"
        },
        "defaultValue": "${each.key}"
      }
    }
PARAMETERS

  policy_rule = templatefile("./policy_rules/tags_inherit_from_subscription.json", {
    roleDefinitionIds_tag_contributor = "TODO",
  })
}
