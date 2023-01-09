data "azurerm_management_group" "pagamenti_servizi_uat" {
  name = "pagamenti_servizi_uat"
}

locals {
  pagamenti_servizi_uat_prefix = "psu"
}

resource "azurerm_management_group_policy_exemption" "pagamenti_servizi_uat_azure_security_benchmark_waiver" {
  name                 = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}${local.pagamenti_servizi_uat_prefix}-waiver"
  management_group_id  = data.azurerm_management_group.pagamenti_servizi_uat.id
  policy_assignment_id = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
  exemption_category   = "Waiver"
  description          = "Motivation at https://pagopa.atlassian.net/wiki/spaces/uatOPS/pages/608960596/Azure+Policy+-+ISO+27001+2013"
  policy_definition_reference_ids = [
    "identityRemoveExternalAccountWithReadPermissionsMonitoring",
    "identityRemoveExternalAccountWithReadPermissionsMonitoringNew",
  ]
}
