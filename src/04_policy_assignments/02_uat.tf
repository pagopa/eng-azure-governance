locals {
  uat_subscriptions = [
    "UAT-CSTAR",
    "UAT-Esercenti",
    "UAT-mil",
    "UAT-SelfCare",
    "UAT-pagoPA",
    "UAT-PCI",
    "UAT-P4PA",
    "UAT-ARC",
    "UAT-FATTURAZIONE",
    "UAT-CRM",
    "UAT-PAY-MONITORING",
  ]
}

module "uat_assignments" {
  source = "./modules/uat"

  for_each = toset(local.uat_subscriptions)

  subscription   = [for s in data.azurerm_subscriptions.available.subscriptions : s if s.display_name == each.value][0]
  location       = var.location
  policy_set_ids = data.terraform_remote_state.policy_set.outputs
}

# data "azurerm_management_group" "uat" {
#   name = "uat"
# }
#
# resource "azurerm_management_group_policy_exemption" "uat_azure_security_benchmark_waiver" {
#   name                            = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}-waiver"
#   management_group_id             = data.azurerm_management_group.uat.id
#   policy_assignment_id            = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
#   exemption_category              = "Waiver"
#   description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
#   policy_definition_reference_ids = local.azure_security_benchmark.policy_uat_waiver_ids
# }
