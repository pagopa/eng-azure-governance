resource "azurerm_policy_set_definition" "root_set" {

  name         = "pagopa_root_set"
  policy_type  = "Custom"
  display_name = "PagoPA policy set/initiatives for all the resources under root sl pagamenti e servizi"
  management_group_name = data.azurerm_management_group.root_sl_pagamenti_servizi.name

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  dynamic "policy_definition_reference" {
    for_each = {
      for item in azurerm_policy_definition.tags_inherit_from_subscription: "${item.id}" => item
    }
    iterator = each
    content {
      policy_definition_id = each.key
      reference_id = each.key
    }
  }
}
