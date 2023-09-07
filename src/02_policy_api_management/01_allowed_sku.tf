data "azurerm_policy_definition" "api_management_allowed_sku" {
  name = "API Management service should use a SKU that supports virtual networks"
}
