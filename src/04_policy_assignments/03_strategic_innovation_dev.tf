data "azurerm_management_group" "strategic_innovation_dev" {
  name = "strategic_innovation_dev"
}

locals {
  strategic_innovation_dev_prefix = "sid"
}

resource "azurerm_management_group_policy_exemption" "strategic_innovation_dev_azure_security_benchmark_waiver" {
  name                 = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}${local.strategic_innovation_dev_prefix}-waiver"
  management_group_id  = data.azurerm_management_group.strategic_innovation_dev.id
  policy_assignment_id = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
  exemption_category   = "Waiver"
  description          = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
  policy_definition_reference_ids = [
    "identityRemoveExternalAccountWithOwnerPermissionsMonitoring",
    "identityRemoveExternalAccountWithOwnerPermissionsMonitoringNew",
    "identityRemoveExternalAccountWithWritePermissionsMonitoring",
    "identityRemoveExternalAccountWithWritePermissionsMonitoringNew",
    "identityRemoveExternalAccountWithReadPermissionsMonitoring",
    "identityRemoveExternalAccountWithReadPermissionsMonitoringNew",
  ]
}
