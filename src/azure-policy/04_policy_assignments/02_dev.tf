module "dev_assignments" {
  source = "./modules/dev"

  for_each = local.subscriptions_by_environment.dev

  subscription   = each.value
  policy_set_ids = local.policy_set_ids
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
