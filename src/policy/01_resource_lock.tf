variable "resource_lock" {
  type        = list(string)
  description = "Resource lock types"
  default = [
    "Microsoft.DocumentDB/databaseAccounts",
    "Microsoft.Storage/storageAccounts",
    "Microsoft.Cache/Redis",
    "Microsoft.Network/publicIPAddresses",
    "Microsoft.DBforPostgreSQL/servers",
    "Microsoft.DBforPostgreSQL/flexibleServers",
    "Microsoft.DataProtection/backupVaults",
    "Microsoft.Network/applicationGateways",
    "Microsoft.OperationalInsights/workspaces",
  ]
}

variable "resource_lock_role_id" {
  type        = string
  description = "Resource lock role for managed identity https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles"
  default     = "18d7d88d-d35e-4fb5-a5c3-7773c20a72d9" # User Access Administrator
}

resource "azurerm_policy_definition" "resource_lock" {
  for_each = toset(var.resource_lock)

  name                = "pagopa_resource_lock_${replace(each.key, "/", "_")}"
  policy_type         = var.policy_type
  mode                = "Indexed"
  display_name        = "PagoPA: Resource lock ${replace(each.key, "/", "_")}"
  management_group_id = data.azurerm_management_group.root_pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0"
    }
METADATA

  policy_rule = <<POLICY_RULE
    {
      "if": {
        "field": "type",
        "equals": "${each.key}"
      },
      "then": {
        "effect": "deployIfNotExists",
        "details": {
          "type": "Microsoft.Authorization/locks",
          "roleDefinitionIds": [
            "/providers/Microsoft.Authorization/roleDefinitions/${var.resource_lock_role_id}"
          ],
          "existenceCondition": {
            "field": "Microsoft.Authorization/locks/level",
            "equals": "CanNotDelete"
          },
          "deployment": {
            "properties": {
              "mode": "Incremental",
              "parameters": {
                "resourceName": {
                  "value": "[field('name')]"
                }
              },
              "template": {
                "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
                "contentVersion": "1.0.0.0",
                "parameters": {
                  "resourceName": {
                    "type": "string"
                  }
                },
                "resources": [
                  {
                    "type": "Microsoft.Authorization/locks",
                    "apiVersion": "2016-09-01",
                    "name": "[parameters('resourceName')]",
                    "scope": "[format('${each.key}/{0}', parameters('resourceName'))]",
                    "properties": {
                      "level": "CanNotDelete"
                    }
                  }
                ]
              }
            }
          }
        }
      }
    }
POLICY_RULE
}

output "resource_lock_ids" {
  value = [
    for resource_lock in azurerm_policy_definition.resource_lock : resource_lock.id
  ]
}