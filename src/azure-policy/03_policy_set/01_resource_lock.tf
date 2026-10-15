locals {
  resource_lock = {
    metadata_category_name = "pagopa_prod"
    types = [
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
      "Microsoft.Cdn/profiles",
      "Microsoft.KeyVault/vaults",
      "Microsoft.EventHub/Namespaces",
      "Microsoft.EventHub/namespaces/eventhubs",
      "Microsoft.DataFactory/factories",
      "Microsoft.Kusto/Clusters",
      "Microsoft.ManagedIdentity/userAssignedIdentities",
      "Microsoft.NotificationHubs/namespaces",
      "Microsoft.NotificationHubs/namespaces/notificationHubs",
    ]
  }
}

# Policy definitions are created in 02_policy_resource_lock, lookup by the same name formula
data "azurerm_policy_definition" "resource_lock" {
  for_each = toset(local.resource_lock.types)

  name                  = "lock${replace(replace(each.key, "/", ""), "Microsoft.", "")}"
  management_group_name = data.azurerm_management_group.pagopa.name
}

resource "azurerm_policy_set_definition" "resource_lock" {
  name                = "resource_lock"
  policy_type         = "Custom"
  display_name        = "PagoPA Resource lock"
  management_group_id = data.azurerm_management_group.pagopa.id

  metadata = jsonencode({
    category = local.resource_lock.metadata_category_name
    version  = "v1.0.0"
    ASC      = "true"
  })

  dynamic "policy_definition_reference" {
    for_each = [for p in data.azurerm_policy_definition.resource_lock : p.id]
    content {
      policy_definition_id = policy_definition_reference.value
      parameter_values     = jsonencode({})
    }
  }
}

output "resource_lock_id" {
  value = azurerm_policy_set_definition.resource_lock.id
}
