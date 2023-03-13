data "azurerm_management_group" "pagamenti_servizi_pci_uat" {
  name = "pagamenti_servizi_pci_uat"
}

locals {
  pagamenti_servizi_pci_uat_prefix                      = "pciu"
  pagamenti_servizi_pci_uat_audit_logs_pci_workspace_id = "/subscriptions/94004462-d636-48bc-aa63-ce22a99d6bf2/resourcegroups/pci-d-weu-core-monitor-rg/providers/microsoft.operationalinsights/workspaces/pci-d-weu-core-law"
  pagamenti_servizi_pci_uat_audit_logs_pci_storage_primary_region = {
    storage_id = "/subscriptions/ac17914c-79bf-48fa-831e-1359ef74c1d5/resourcegroups/devopslab-logs/providers/Microsoft.Storage/storageAccounts/devopslablogs"
    location   = "westeurope"
  }
  pagamenti_servizi_pci_uat_audit_logs_pci_storage_secondary_region = {
    storage_id = "novalue"
    location   = "northeurope"
  }
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_pci_uat_pcidssv4" {
  name                 = "${local.pagamenti_servizi_pci_uat_prefix}pcidssv4"
  display_name         = "PCI DSS v4"
  policy_definition_id = local.pci_dss_v4.id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_pci_uat.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_pci_uat_audit_logs" {
  name                 = "${local.pagamenti_servizi_pci_uat_prefix}auditlogs"
  display_name         = "PagoPA Audit logs"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.audit_logs_pci_id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_pci_uat.id

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

  parameters = <<PARAMETERS
    {
        "logAnalyticsId": {
            "value": "${local.pagamenti_servizi_pci_uat_audit_logs_pci_workspace_id}"
        },
        "storageAccountPrimaryRegionId": {
            "value": "${local.pagamenti_servizi_pci_uat_audit_logs_pci_storage_primary_region.storage_id}"
        },
        "storageAccountPrimaryRegionLocation": {
            "value": "${local.pagamenti_servizi_pci_uat_audit_logs_pci_storage_primary_region.location}"
        },
        "storageAccountSecondaryRegionId": {
            "value": "${local.pagamenti_servizi_pci_uat_audit_logs_pci_storage_secondary_region.storage_id}"
        },
        "storageAccountSecondaryRegionLocation": {
            "value": "${local.pagamenti_servizi_pci_uat_audit_logs_pci_storage_secondary_region.location}"
        }
    }
  PARAMETERS
}

resource "azurerm_role_assignment" "pagamenti_servizi_pci_uat_audit_logs_monitoring_contributor" {
  scope                = data.azurerm_management_group.pagamenti_servizi_pci_uat.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_pci_uat_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "pagamenti_servizi_pci_uat_audit_logs_contributor_log_analytics" {
  scope                = local.pagamenti_servizi_pci_uat_audit_logs_pci_workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_pci_uat_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "pagamenti_servizi_pci_uat_audit_logs_contributor_storage_westeurope" {
  scope                = local.pagamenti_servizi_pci_uat_audit_logs_pci_storage_primary_region.storage_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_pci_uat_audit_logs.identity[0].principal_id
}
