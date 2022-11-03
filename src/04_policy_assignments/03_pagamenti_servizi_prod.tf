resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_prod_resource_lock" {
  name                 = "pspresourcelock"
  display_name         = "PagoPA Resource lock"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.resource_lock_id
  management_group_id  = data.azurerm_management_group.prod_sl_pagamenti_servizi.id

  location = var.location
  enforce  = true
  identity {
    type = "SystemAssigned"
  }

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_role_assignment" "pagamenti_servizi_prod_resource_lock_contributor" {
  scope                = data.azurerm_management_group.prod_sl_pagamenti_servizi.id
  role_definition_name = "PagoPA Resource Lock Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_prod_resource_lock.identity[0].principal_id
}
