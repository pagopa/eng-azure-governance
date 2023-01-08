data "azurerm_management_group" "pagamenti_servizi_prod" {
  name = "pagamenti_servizi_prod"
}

locals {
  pagamenti_servizi_prod_prefix = "psp"
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_prod_iso_27001_2013" {
  name                 = "${local.pagamenti_servizi_prod_prefix}iso270012013"
  display_name         = "ISO 27001:2013"
  policy_definition_id = local.intiative_ids.iso_27001_2013
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_prod.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_exemption" "pagamenti_servizi_prod_iso_27001_2013" {
  name                 = "${azurerm_management_group_policy_assignment.pagamenti_servizi_prod_iso_27001_2013.name}"
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_prod.id
  policy_assignment_id = azurerm_management_group_policy_assignment.pagamenti_servizi_prod_iso_27001_2013.id
  exemption_category   = "Mitigated"
  description          = "Mitigated with Google MFA"
  policy_definition_reference_ids = [
    "/providers/Microsoft.Authorization/policyDefinitions/e3576e28-8b17-4677-84c3-db2990658d64", # MFA should be enabled on accounts with read permissions on your subscription
    "/providers/Microsoft.Authorization/policyDefinitions/9297c21d-2ed6-4474-b48f-163f75654ce3", # MFA should be enabled for accounts with write permissions on your subscription
    "/providers/Microsoft.Authorization/policyDefinitions/aa633080-8b72-40c4-a2d7-d00c03e80bed", # MFA should be enabled on accounts with owner permissions on your subscription
    "/providers/Microsoft.Authorization/policyDefinitions/4f11b553-d42e-4e3a-89be-32ca364cad4c", # A maximum of 3 owners should be designated for your subscription
  ]
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_prod_resource_lock" {
  name                 = "${local.pagamenti_servizi_prod_prefix}resourcelock"
  display_name         = "PagoPA Resource lock"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.resource_lock_id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_prod.id

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
  scope                = data.azurerm_management_group.pagamenti_servizi_prod.id
  role_definition_name = "PagoPA Resource Lock Contributor"
  principal_id         = azurerm_management_group_policy_assignment.pagamenti_servizi_prod_resource_lock.identity[0].principal_id
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_prod_audit_logs" {
  name                 = "${local.pagamenti_servizi_prod_prefix}auditlogs"
  display_name         = "PagoPA Audit logs"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.audit_logs_id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_prod.id

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
  scope                = data.azurerm_management_group.pagamenti_servizi_prod.id
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

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_prod_storage_account" {
  name                 = "${local.pagamenti_servizi_prod_prefix}stac"
  display_name         = "PagoPA Storage Account"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.storage_account_prod_id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_prod_application_gateway" {
  name                 = "${local.pagamenti_servizi_prod_prefix}appgw"
  display_name         = "PagoPA Application Gateway"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.application_gateway_prod_id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_prod.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}
