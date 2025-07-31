resource "azurerm_role_definition" "storage_blob_contributor" {
  name        = "PagoPA Storage Blob Tags Contributor"
  scope       = data.azurerm_management_group.pagopa.id
  description = "Role for managing tags of blobs in storage"

  permissions {
    data_actions = [
      "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/read", # read tags of blobs in storage
      "Microsoft.Storage/storageAccounts/blobServices/containers/blobs/tags/write" # write tags of blobs in storage
    ]
  }
}
