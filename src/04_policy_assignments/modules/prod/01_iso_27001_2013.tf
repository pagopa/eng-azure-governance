resource "azurerm_subscription_policy_assignment" "iso_27001_2013" {
  name                 = substr("${local.prefix}iso270012013", 0, 64)
  display_name         = "ISO 27001:2013"
  policy_definition_id = "/providers/Microsoft.Authorization/policySetDefinitions/89c6cddc-1c73-4ac1-b19c-54d1a15a42f2"
  subscription_id      = var.subscription.id
  location             = var.location
  enforce              = false

  parameters = jsonencode({
    metricsEnabled-7f89b1eb-583c-429a-8828-af049802c1d9 = {
      value = false
    }
  })

  identity {
    type = "SystemAssigned"
  }
}
