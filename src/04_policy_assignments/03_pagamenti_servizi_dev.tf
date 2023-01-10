data "azurerm_management_group" "pagamenti_servizi_dev" {
  name = "pagamenti_servizi_dev"
}

locals {
  pagamenti_servizi_dev_prefix = "psd"
}

resource "azurerm_management_group_policy_exemption" "pagamenti_servizi_dev_azure_security_benchmark_waiver" {
  name                            = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}${local.pagamenti_servizi_dev_prefix}-waiver"
  management_group_id             = data.azurerm_management_group.pagamenti_servizi_dev.id
  policy_assignment_id            = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
  exemption_category              = "Waiver"
  description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
  policy_definition_reference_ids = local.azure_security_benchmark.policy_dev_waiver_ids
}
