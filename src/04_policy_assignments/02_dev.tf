locals {
  dev_subscriptions = [
    "DEV-CSTAR",
    "DEV-FATTURAZIONE",
    "DEV-IO",
    "DEV-mil",
    "DEV-SelfCare",
    "DEV-pagoPA",
    "DEV-PCI",
    "DevOpsLab",
    "DEV-Assistenza",
    "DEV-P4PA",
    "DEV-ARC",
    "DEV-GRC",
    "DEV-ICT",
    "DEV-CRM",
    "DEV-DEVEX",
    "DEV-PLATFORM-SM",
    "DEV-PAY-MONITORING",
  ]
}

module "dev_assignments" {
  source = "./modules/dev"

  for_each = toset(local.dev_subscriptions)

  subscription   = [for s in data.azurerm_subscriptions.available.subscriptions : s if s.display_name == each.value][0]
  location       = var.location
  policy_set_ids = data.terraform_remote_state.policy_set.outputs
}

# data "azurerm_management_group" "dev" {
#   name = "dev"
# }
#
# resource "azurerm_management_group_policy_exemption" "dev_azure_security_benchmark_waiver" {
#   name                            = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}-waiver"
#   management_group_id             = data.azurerm_management_group.dev.id
#   policy_assignment_id            = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
#   exemption_category              = "Waiver"
#   description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
#   policy_definition_reference_ids = local.azure_security_benchmark.policy_dev_waiver_ids
# }
