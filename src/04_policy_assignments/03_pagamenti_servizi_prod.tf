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

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_prod_audit_logs" {
  name                 = "pspauditlogs"
  display_name         = "PagoPA Audit logs"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.audit_logs_id
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

resource "azurerm_role_assignment" "pagamenti_servizi_prod_audit_logs_monitoring_contributor" {
  scope                = data.azurerm_management_group.prod_sl_pagamenti_servizi.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_prod_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "pagamenti_servizi_prod_audit_logs_contributor_log_analytics" {
  scope                = data.terraform_remote_state.policy_set.outputs.audit_logs_workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_prod_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "pagamenti_servizi_prod_audit_logs_contributor_storage_westeurope" {
  scope                = data.terraform_remote_state.policy_set.outputs.audit_logs_storage_id_westeurope
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_prod_audit_logs.identity[0].principal_id
}

# resource "azurerm_role_assignment" "pagamenti_servizi_prod_audit_logs_contributor_storage_northeurope" {
#   scope                = data.terraform_remote_state.policy_set.outputs.audit_logs_storage_id_northeurope
#   role_definition_name = "Log Analytics Contributor"
#   principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_prod_audit_logs.identity[0].principal_id
# }
