resource "azurerm_policy_set_definition" "resource_lock" {
  name                = "resource_lock"
  policy_type         = var.policy_type
  display_name        = "PagoPA Resource lock"
  management_group_id = data.azurerm_management_group.root_pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  dynamic "policy_definition_reference" {
    for_each = data.terraform_remote_state.policy.outputs.resource_lock_ids
    content {
      policy_definition_id = policy_definition_reference.value
    }
  }
}

output "resource_lock_id" {
  value = azurerm_policy_set_definition.resource_lock.id
}
