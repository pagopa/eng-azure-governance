resource "azurerm_role_definition" "iac_reader" {
  name        = "PagoPA IaC Reader"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Infrastructure as Code read-only role"

  permissions {
    actions = [
      "Microsoft.Resources/deployments/exportTemplate/action",                           # read arm template deployments
      "Microsoft.Web/sites/config/list/action",                                          # read app config for function app, app service
      "Microsoft.Web/sites/slots/config/list/action",                                    # read app config for function app, app service slots
      "Microsoft.ContainerService/managedClusters/read",                                 # help to generate cluster credentials
      "Microsoft.ContainerService/managedClusters/listClusterUserCredential/action",     # help to generate cluster credentials
      "Microsoft.ContainerService/managedClusters/accessProfiles/listCredential/action", # help to generate cluster credentials and read cluster roles
      "Microsoft.EventHub/namespaces/eventhubs/authorizationRules/listKeys/action",      #help to list key for event hub connection (mandatory for tf:azurerm_eventhub_authorization_rule)
      "Microsoft.ServiceBus/namespaces/authorizationRules/listKeys/action",              #help to list key for service bus connection
      "Microsoft.ServiceBus/namespaces/queues/authorizationRules/listKeys/action",
      "Microsoft.Cache/redis/listKeys/action",
      "Microsoft.Web/sites/host/listkeys/action",
      "Microsoft.NotificationHubs/namespaces/notificationHubs/pnsCredentials/action",              #list NotificationHub PNS credentials
      "Microsoft.NotificationHubs/namespaces/notificationHubs/authorizationRules/listKeys/action", #list NotificationHub keys
    ]
  }
}
