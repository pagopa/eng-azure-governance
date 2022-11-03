# variable "workspaceid" {
#   type        = string
#   default     = "/subscriptions/ac17914c-79bf-48fa-831e-1359ef74c1d5/resourcegroups/dvopla-d-monitor-rg/providers/microsoft.operationalinsights/workspaces/dvopla-d-law"
#   description = "description"
# }

# variable "storageid" {
#   type        = string
#   default     = "/subscriptions/ac17914c-79bf-48fa-831e-1359ef74c1d5/resourceGroups/dvopla-d-monitor-rg/providers/Microsoft.Storage/storageAccounts/dvopladsecmonitorst"
#   description = "description"
# }

# locals {
#   audit_logs = {
#     workspaceid_policy_definition_reference_id = "workspaceid"
#     storageid_policy_definition_reference_id = "storageid"
#   }
# }

# resource "azurerm_policy_set_definition" "audit_logs" {
#   name                = "audit_logs"
#   policy_type         = var.policy_type
#   display_name        = "PagoPA Audit logs"
#   management_group_id = data.azurerm_management_group.root_pagopa.id

#   metadata = <<METADATA
#     {
#         "category": "${var.metadata_category_name}",
#         "version": "v1.0.0",
#         "parameterScopes": {
#           "workspaceid : ${local.audit_logs.workspaceid_policy_definition_reference_id}": "${data.azurerm_management_group.root_pagopa.id}"
#         }
#     }
# METADATA

#   dynamic "policy_definition_reference" {
#     for_each = data.terraform_remote_state.policy.outputs.audit_logs_ids
#     content {
#       policy_definition_id = policy_definition_reference.value
#       reference_id = local.audit_logs.workspaceid_policy_definition_reference_id
#       parameter_values     = <<VALUE
#     {
#       "logAnalytics": {
#         "value": "${var.workspaceid}"
#       },
#       "storageAccount": {
#         "value": "${var.storageid}"
#       }
#     }
#     VALUE
#     }
#   }
# }
