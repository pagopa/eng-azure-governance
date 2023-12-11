data "azurerm_management_group" "uat" {
  name = "uat"
}

locals {
  uat_prefix = "uat"
}

resource "azurerm_management_group_policy_exemption" "uat_azure_security_benchmark_waiver" {
  name                            = "${azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.name}-waiver"
  management_group_id             = data.azurerm_management_group.uat.id
  policy_assignment_id            = azurerm_management_group_policy_assignment.pagopa_azure_security_benchmark.id
  exemption_category              = "Waiver"
  description                     = "Motivation at https://pagopa.atlassian.net/wiki/spaces/DEVOPS/pages/608960613/Azure+Policy+-+Azure+Security+Benchmark"
  policy_definition_reference_ids = local.azure_security_benchmark.policy_uat_waiver_ids
}

resource "azurerm_management_group_policy_assignment" "uat_app_service" {
  name                 = "${local.uat_prefix}appservice"
  display_name         = "PagoPA App Service"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.app_service_uat_id
  management_group_id  = data.azurerm_management_group.uat.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "uat_redis" {
  name                 = "${local.uat_prefix}redis"
  display_name         = "PagoPA Redis"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.redis_uat_id
  management_group_id  = data.azurerm_management_group.uat.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "uat_virtual_machine" {
  name                 = "${local.uat_prefix}virtualmachine"
  display_name         = "PagoPA Virtual Machine"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.virtual_machine_uat_id
  management_group_id  = data.azurerm_management_group.uat.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "uat_virtual_machine_scael_set" {
  name                 = "${local.uat_prefix}vmscaleset"
  display_name         = "PagoPA Virtual Machine Scale Set"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.virtual_machine_scale_set_uat_id
  management_group_id  = data.azurerm_management_group.uat.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "uat_api_management" {
  name                 = "${local.uat_prefix}apimanagement"
  display_name         = "PagoPA Api Management"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.api_management_uat_id
  management_group_id  = data.azurerm_management_group.uat.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}

resource "azurerm_management_group_policy_assignment" "uat_log_analytics" {
  name                 = "${local.uat_prefix}loganalytics"
  display_name         = "PagoPA Log Analytics"
  policy_definition_id = data.terraform_remote_state.policy_set.outputs.log_analytics_uat_id
  management_group_id  = data.azurerm_management_group.uat.id

  enforce = true

  metadata = jsonencode({
    category = var.metadata_category_name
    version  = "v1.0.0"
  })
}
