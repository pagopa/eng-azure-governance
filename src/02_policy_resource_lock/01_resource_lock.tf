variable "resource_lock_types" {
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
    "Microsoft.Network/natGateways",
    "Microsoft.Network/virtualNetworkGateways",
    "Microsoft.OperationalInsights/workspaces",
    "microsoft.insights/components",
    "Microsoft.ContainerService/ManagedClusters",
    "Microsoft.Cdn/profiles/endpoints",
    "Microsoft.KeyVault/vaults",
    "Microsoft.EventHub/Namespaces",
    "Microsoft.EventHub/namespaces/eventhubs",
    "Microsoft.DataFactory/factories",
    "Microsoft.Kusto/Clusters",
    "Microsoft.ManagedIdentity/userAssignedIdentities",
    "Microsoft.NotificationHubs/namespaces",
    "Microsoft.NotificationHubs/namespaces/notificationHubs",
    # "Microsoft.Network/dnszones", to verify, cannot delete records
    # "Microsoft.Network/privateDnsZones", to verify, cannot delete records
  ]
}

data "azurerm_role_definition" "resource_lock_contributor" {
  name = "PagoPA Resource Lock Contributor"
}

resource "azurerm_policy_definition" "resource_lock" {
  for_each = toset(var.resource_lock_types)

  name                = "lock${replace(replace(each.key, "/", ""), "Microsoft.", "")}"
  policy_type         = "Custom"
  mode                = "Indexed"
  display_name        = "PagoPA Add resource lock to ${replace(replace(each.key, "/", "_"), "Microsoft.", "")}"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = <<METADATA
    {
        "category": "${var.metadata_category_name}",
        "version": "v1.0.0",
        "securityCenter": {
		      "RemediationDescription": "Add resource lock to ${each.key}",
		      "Severity": "High"
        }
    }
METADATA

  policy_rule = templatefile("./policy_rules/resource_lock.json", {
    resource_lock_types                         = each.key,
    roleDefinitionIds_resource_lock_contributor = data.azurerm_role_definition.resource_lock_contributor.id,
  })

  #   policy_rule = <<POLICY_RULE
  #     {
  #       "if": {
  #         "field": "type",
  #         "equals": "${each.key}"
  #       },
  #       "then": {
  #         "effect": "deployIfNotExists",
  #         "details": {
  #           "type": "Microsoft.Authorization/locks",
  #           "roleDefinitionIds": [
  #             "${data.azurerm_role_definition.resource_lock_contributor.id}"
  #           ],
  #           "existenceCondition": {
  #             "field": "Microsoft.Authorization/locks/level",
  #             "equals": "CanNotDelete"
  #           },
  #           "deployment": {
  #             "properties": {
  #               "mode": "Incremental",
  #               "parameters": {
  #                 "resourceName": {
  #                   "value": "[field('name')]"
  #                 }
  #               },
  #               "template": {
  #                 "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  #                 "contentVersion": "1.0.0.0",
  #                 "parameters": {
  #                   "resourceName": {
  #                     "type": "string"
  #                   }
  #                 },
  #                 "resources": [
  #                   {
  #                     "type": "Microsoft.Authorization/locks",
  #                     "apiVersion": "2016-09-01",
  #                     "name": "[parameters('resourceName')]",
  #                     "scope": "[format('${each.key}/{0}', parameters('resourceName'))]",
  #                     "properties": {
  #                       "level": "CanNotDelete"
  #                     }
  #                   }
  #                 ]
  #               }
  #             }
  #           }
  #         }
  #       }
  #     }
  # POLICY_RULE
}