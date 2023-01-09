data "azurerm_management_group" "strategic_innovation_prod" {
  name = "strategic_innovation_prod"
}

resource "azurerm_management_group_policy_assignment" "strategic_innovation_prod_iso_27001_2013" {
  name                 = "sipiso270012013"
  display_name         = "ISO 27001:2013"
  policy_definition_id = local.intiative_ids.iso_27001_2013
  management_group_id  = data.azurerm_management_group.strategic_innovation_prod.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_exemption" "strategic_innovation_prod_iso_27001_2013_mitigated" {
  name                 = "${azurerm_management_group_policy_assignment.strategic_innovation_prod_iso_27001_2013.name}-mitigated"
  management_group_id  = data.azurerm_management_group.strategic_innovation_prod.id
  policy_assignment_id = azurerm_management_group_policy_assignment.strategic_innovation_prod_iso_27001_2013.id
  exemption_category   = "Mitigated"
  description          = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960596/Azure+Policy+-+ISO+27001+2013"
  policy_definition_reference_ids = [
    "PreviewAuditAccountsWithOwnerPermissionsWhoAreNotMfaEnabledOnASubscription", # MFA should be enabled on accounts with read permissions on your subscription
    "PreviewAuditAccountsWithWritePermissionsWhoAreNotMfaEnabledOnASubscription", # MFA should be enabled for accounts with write permissions on your subscription
    "PreviewAuditAccountsWithReadPermissionsWhoAreNotMfaEnabledOnASubscription",  # MFA should be enabled on accounts with owner permissions on your subscription
  ]
}

resource "azurerm_management_group_policy_exemption" "strategic_innovation_prod_iso_27001_2013_waiver" {
  name                 = "${azurerm_management_group_policy_assignment.strategic_innovation_prod_iso_27001_2013.name}-waiver"
  management_group_id  = data.azurerm_management_group.strategic_innovation_prod.id
  policy_assignment_id = azurerm_management_group_policy_assignment.strategic_innovation_prod_iso_27001_2013.id
  exemption_category   = "Waiver"
  description          = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960596/Azure+Policy+-+ISO+27001+2013"
  policy_definition_reference_ids = [
    "PreviewAuditMaximumNumberOfOwnersForASubscription", # A maximum of 3 owners should be designated for your subscription
  ]
}

resource "azurerm_management_group_policy_assignment" "strategic_innovation_prod_resource_lock" {
  name                 = "sipresourcelock"
  display_name         = "PagoPA Resource lock"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.resource_lock_id
  management_group_id  = data.azurerm_management_group.strategic_innovation_prod.id

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

resource "azurerm_role_assignment" "strategic_innovation_prod_resource_lock_contributor" {
  scope                = data.azurerm_management_group.strategic_innovation_prod.id
  role_definition_name = "PagoPA Resource Lock Contributor"
  principal_id         = azurerm_management_group_policy_assignment.strategic_innovation_prod_resource_lock.identity[0].principal_id
}

resource "azurerm_management_group_policy_assignment" "strategic_innovation_prod_audit_logs" {
  name                 = "sipauditlogs"
  display_name         = "PagoPA Audit logs"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.audit_logs_id
  management_group_id  = data.azurerm_management_group.strategic_innovation_prod.id

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

resource "azurerm_role_assignment" "strategic_innovation_prod_audit_logs_monitoring_contributor" {
  scope                = data.azurerm_management_group.strategic_innovation_prod.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_management_group_policy_assignment.strategic_innovation_prod_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "strategic_innovation_prod_audit_logs_contributor_log_analytics" {
  scope                = data.terraform_remote_state.policy_set.outputs.audit_logs_workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.strategic_innovation_prod_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "strategic_innovation_prod_audit_logs_contributor_storage_westeurope" {
  scope                = data.terraform_remote_state.policy_set.outputs.audit_logs_storage_id_westeurope
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.strategic_innovation_prod_audit_logs.identity[0].principal_id
}
