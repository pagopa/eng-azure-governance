resource "azurerm_user_assigned_identity" "prod" {
  name                = "${local.app_name}-prod"
  location            = data.azurerm_resource_group.identity.location
  resource_group_name = data.azurerm_resource_group.identity.name
}

resource "azurerm_federated_identity_credential" "prod" {
  name                = "github-federated-environment-${var.env}"
  resource_group_name = data.azurerm_resource_group.identity.name
  audience            = ["api://AzureADTokenExchange"]
  issuer              = "https://token.actions.githubusercontent.com"
  parent_id           = azurerm_user_assigned_identity.prod.id
  subject             = "repo:${var.github.org}/${var.github.repository}:environment:${var.env}"
}

output "azure_main" {
  value = {
    app_name       = azurerm_user_assigned_identity.prod.name
    client_id      = azurerm_user_assigned_identity.prod.client_id
    application_id = azurerm_user_assigned_identity.prod.client_id
    object_id      = azurerm_user_assigned_identity.prod.principal_id
  }
}
