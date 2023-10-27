data "azurerm_management_group" "prod_pci" {
  name = "prod_pci"
}

locals {
  prod_pci_prefix                      = "pcip"
  prod_pci_audit_logs_pci_workspace_id = data.terraform_remote_state.policy_set.outputs.audit_logs_workspace_id
  prod_pci_audit_logs_pci_storage_primary_region = {
    storage_id = data.terraform_remote_state.policy_set.outputs.audit_logs_storage_id_westeurope
    location   = "westeurope"
  }
  prod_pci_audit_logs_pci_storage_secondary_region = {
    storage_id = "novalue"
    location   = "northeurope"
  }
  prod_pci_metrics_logs_pci_workspace_id = data.terraform_remote_state.policy_set.outputs.audit_logs_workspace_id
}

resource "azurerm_management_group_policy_assignment" "prod_pci_pcidssv4" {
  name                 = "${local.prod_pci_prefix}pcidssv4"
  display_name         = "PCI DSS v4"
  policy_definition_id = local.pci_dss_v4.id
  management_group_id  = data.azurerm_management_group.prod_pci.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_assignment" "prod_pci_audit_logs" {
  name                 = "${local.prod_pci_prefix}auditlogs"
  display_name         = "PagoPA Audit logs"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.audit_logs_pci_id
  management_group_id  = data.azurerm_management_group.prod_pci.id

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

resource "azurerm_role_assignment" "prod_pci_audit_logs_monitoring_contributor" {
  scope                = data.azurerm_management_group.prod_pci.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_pci_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "prod_pci_audit_logs_contributor_log_analytics" {
  scope                = local.prod_pci_audit_logs_pci_workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_pci_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "prod_pci_audit_logs_contributor_storage_westeurope" {
  scope                = local.prod_pci_audit_logs_pci_storage_primary_region.storage_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_pci_audit_logs.identity[0].principal_id
}

resource "azurerm_management_group_policy_assignment" "prod_pci_metrics_logs" {
  name                 = "${local.prod_pci_prefix}metricslogs"
  display_name         = "PagoPA Metric logs"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.metrics_logs_id
  management_group_id  = data.azurerm_management_group.prod_pci.id

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
            "value": "${local.prod_pci_metrics_logs_pci_workspace_id}"
        }
    }
  PARAMETERS
}

resource "azurerm_role_assignment" "prod_pci_metrics_logs_monitoring_contributor" {
  scope                = data.azurerm_management_group.prod_pci.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_pci_metrics_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "prod_pci_metrics_logs_contributor_log_analytics" {
  scope                = local.prod_pci_metrics_logs_pci_workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.prod_pci_metrics_logs.identity[0].principal_id
}

resource "azurerm_management_group_policy_assignment" "prod_pci_storage_account" {
  name                 = "${local.prod_pci_prefix}stac"
  display_name         = "PagoPA Storage Account"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.storage_account_prod_id
  management_group_id  = data.azurerm_management_group.prod_pci.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}
