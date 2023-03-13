data "azurerm_management_group" "pagamenti_servizi_pci_prod" {
  name = "pagamenti_servizi_pci_prod"
}

locals {
  pagamenti_servizi_pci_prod_prefix                      = "pcip"
  pagamenti_servizi_pci_prod_audit_logs_pci_workspace_id = data.terraform_remote_state.policy_set.outputs.audit_logs_workspace_id
  pagamenti_servizi_pci_prod_audit_logs_pci_storage_primary_region = {
    storage_id = data.terraform_remote_state.policy_set.outputs.audit_logs_storage_id_westeurope
    location   = "westeurope"
  }
  pagamenti_servizi_pci_prod_audit_logs_pci_storage_secondary_region = {
    storage_id = "novalue"
    location   = "northeurope"
  }
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_pci_prod_pcidssv4" {
  name                 = "${local.pagamenti_servizi_pci_prod_prefix}pcidssv4"
  display_name         = "PCI DSS v4"
  policy_definition_id = local.pci_dss_v4.id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_pci_prod.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_pci_prod_resource_lock" {
  name                 = "${local.pagamenti_servizi_pci_prod_prefix}resourcelock"
  display_name         = "PagoPA Resource lock"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.resource_lock_id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_pci_prod.id

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

resource "azurerm_role_assignment" "pagamenti_servizi_pci_prod_resource_lock_contributor" {
  scope                = data.azurerm_management_group.pagamenti_servizi_pci_prod.id
  role_definition_name = "PagoPA Resource Lock Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_pci_prod_resource_lock.identity[0].principal_id
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_pci_prod_audit_logs" {
  name                 = "${local.pagamenti_servizi_pci_prod_prefix}auditlogs"
  display_name         = "PagoPA Audit logs"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.audit_logs_pci_id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_pci_prod.id

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

resource "azurerm_role_assignment" "pagamenti_servizi_pci_prod_audit_logs_monitoring_contributor" {
  scope                = data.azurerm_management_group.pagamenti_servizi_pci_prod.id
  role_definition_name = "PagoPA Audit Logs Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_pci_prod_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "pagamenti_servizi_pci_prod_audit_logs_contributor_log_analytics" {
  scope                = local.pagamenti_servizi_pci_prod_audit_logs_pci_workspace_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_pci_prod_audit_logs.identity[0].principal_id
}

resource "azurerm_role_assignment" "pagamenti_servizi_pci_prod_audit_logs_contributor_storage_westeurope" {
  scope                = local.pagamenti_servizi_pci_prod_audit_logs_pci_storage_primary_region.storage_id
  role_definition_name = "Log Analytics Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_pci_prod_audit_logs.identity[0].principal_id
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_pci_prod_storage_account" {
  name                 = "${local.pagamenti_servizi_pci_prod_prefix}stac"
  display_name         = "PagoPA Storage Account"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.storage_account_prod_id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_pci_prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_pci_prod_application_gateway" {
  name                 = "${local.pagamenti_servizi_pci_prod_prefix}appgw"
  display_name         = "PagoPA Application Gateway"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.application_gateway_prod_id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_pci_prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}
