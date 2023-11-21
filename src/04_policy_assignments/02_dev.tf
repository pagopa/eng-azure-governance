data "azurerm_management_group" "dev" {
  name = "dev"
}

locals {
  dev_prefix = "dev"
}

resource "azurerm_management_group_policy_exemption" "dev_azure_security_benchmark_waiver" {
  name                            = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}-waiver"
  management_group_id             = data.azurerm_management_group.dev.id
  policy_assignment_id            = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
  exemption_category              = "Waiver"
  description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
  policy_definition_reference_ids = local.azure_security_benchmark.policy_dev_waiver_ids
}

resource "azurerm_management_group_policy_assignment" "dev_app_service" {
  name                 = "${local.dev_prefix}appservice"
  display_name         = "PagoPA App Service"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.app_service_dev_id
  management_group_id  = data.azurerm_management_group.dev.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "dev_redis" {
  name                 = "${local.dev_prefix}redis"
  display_name         = "PagoPA Redis"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.redis_dev_id
  management_group_id  = data.azurerm_management_group.dev.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "dev_virtual_machine" {
  name                 = "${local.dev_prefix}virtualmachine"
  display_name         = "PagoPA Virtual Machine"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.virtual_machine_dev_id
  management_group_id  = data.azurerm_management_group.dev.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "dev_virtual_machine_scael_set" {
  name                 = "${local.dev_prefix}vmscaleset"
  display_name         = "PagoPA Virtual Machine Scale Set"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.virtual_machine_scale_set_dev_id
  management_group_id  = data.azurerm_management_group.dev.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "dev_api_management" {
  name                 = "${local.dev_prefix}apimanagement"
  display_name         = "PagoPA Api Management"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.api_management_dev_id
  management_group_id  = data.azurerm_management_group.dev.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "dev_log_analytics" {
  name                 = "${local.dev_prefix}loganalytics"
  display_name         = "PagoPA Log Analytics"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.log_analytics_dev_id
  management_group_id  = data.azurerm_management_group.dev.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
