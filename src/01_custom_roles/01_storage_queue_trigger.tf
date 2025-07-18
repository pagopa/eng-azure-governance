resource "azurerm_role_definition" "storage_queue_trigger" {
  name        = "PagoPA Storage Queue Data Message Contributor"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Role for managing visibility timeout of messages in storage queues"

  permissions {
    data_actions = [
      "Microsoft.Storage/storageAccounts/queueServices/queues/messages/write",         # set visibility timeout of messages in storage queues
      "Microsoft.Storage/storageAccounts/queueServices/queues/messages/delete",        # delete messages in storage queues
      "Microsoft.Storage/storageAccounts/queueServices/queues/messages/process/action" # process messages in storage queues
    ]
  }
}
