data "azurerm_management_group" "pagopa" {
  name = "pagopa"
}

locals {
  pagopa_prefix = "pagopa"
}

resource "azurerm_management_group_policy_assignment" "pagopa_data_sovereignty_eu" {
  name                 = "${local.pagopa_prefix}datasovereigntyeu"
  display_name         = "PagoPA Data sovereignty in EU"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.data_sovereignty_eu_id
  management_group_id  = data.azurerm_management_group.pagopa.id

  enforce = true

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
  METADATA
}

resource "azurerm_management_group_policy_assignment" "pagopa_azure_security_benchmark" {
  name                 = "${local.pagopa_prefix}asc"
  display_name         = "Azure Security Benchmark"
  policy_definition_id = local.azure_security_benchmark.id
  management_group_id  = data.azurerm_management_group.pagopa.id

  location = var.location
  enforce  = false
  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_management_group_policy_exemption" "pagopa_azure_security_benchmark_mitigated" {
  name                 = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}-mitigated"
  management_group_id  = data.azurerm_management_group.pagopa.id
  policy_assignment_id = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
  exemption_category   = "Mitigated"
  description          = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
  policy_definition_reference_ids = [
    "identityEnableMFAForOwnerPermissionsMonitoring",
    "identityEnableMFAForOwnerPermissionsMonitoringNew",
    "identityEnableMFAForWritePermissionsMonitoring",
    "identityEnableMFAForWritePermissionsMonitoringEffect",
    "identityEnableMFAForReadPermissionsMonitoring",
    "identityEnableMFAForReadPermissionsMonitoringNew",
  ]
}

resource "azurerm_management_group_policy_exemption" "pagopa_azure_security_benchmark_waiver" {
  name                 = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}-waiver"
  management_group_id  = data.azurerm_management_group.pagopa.id
  policy_assignment_id = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
  exemption_category   = "Waiver"
  description          = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
  policy_definition_reference_ids = [
    "ensureWEBAppHasClientCertificatesIncomingClientCertificatesSetToOnMonitoringEffect",
    "functionAppsShouldHaveClientCertificatesEnabledMonitoringEffect",
  ]
}
