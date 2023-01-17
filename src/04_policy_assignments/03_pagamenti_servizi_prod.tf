data "azurerm_management_group" "pagamenti_servizi_prod" {
  name = "pagamenti_servizi_prod"
}

locals {
  pagamenti_servizi_prod_prefix = "psp"
}

resource "azurerm_management_group_policy_assignment" "pagamenti_servizi_prod_iso_27001_2013" {
  name                 = "${local.pagamenti_servizi_prod_prefix}iso270012013"
  display_name         = "ISO 27001:2013"
  policy_definition_id = local.iso_27001_2013.id
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_prod.id

  parameters = jsonencode(
    {
      metricsEnabled-7f89b1eb-583c-429a-8828-af049802c1d9 = {
        value = false
      }
    }
  )

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_exemption" "pagamenti_servizi_prod_iso_27001_2013_mitigated" {
  name                            = "${azurerm_management_group_policy_assignment.pagamenti_servizi_prod_iso_27001_2013.name}-mitigated"
  management_group_id             = data.azurerm_management_group.pagamenti_servizi_prod.id
  policy_assignment_id            = azurerm_management_group_policy_assignment.pagamenti_servizi_prod_iso_27001_2013.id
  exemption_category              = "Mitigated"
  description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960596/Azure+Policy+-+ISO+27001+2013"
  policy_definition_reference_ids = local.iso_27001_2013.policy_prod_mitigated_ids
}

resource "azurerm_management_group_policy_exemption" "pagamenti_servizi_prod_iso_27001_2013_waiver" {
  name                            = "${azurerm_management_group_policy_assignment.pagamenti_servizi_prod_iso_27001_2013.name}-waiver"
  management_group_id             = data.azurerm_management_group.pagamenti_servizi_prod.id
  policy_assignment_id            = azurerm_management_group_policy_assignment.pagamenti_servizi_prod_iso_27001_2013.id
  exemption_category              = "Waiver"
  description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960596/Azure+Policy+-+ISO+27001+2013"
  policy_definition_reference_ids = local.iso_27001_2013.policy_prod_waiver_ids
}

resource "azurerm_management_group_policy_exemption" "pagamenti_servizi_prod_azure_security_benchmark_waiver" {
  name                            = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}${local.pagamenti_servizi_prod_prefix}-waiver"
  management_group_id             = data.azurerm_management_group.pagamenti_servizi_prod.id
  policy_assignment_id            = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
  exemption_category              = "Waiver"
  description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
  policy_definition_reference_ids = local.azure_security_benchmark.policy_prod_waiver_ids
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
