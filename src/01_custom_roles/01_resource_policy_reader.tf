# resource "azurerm_role_definition" "resource_policy_reader" {
#   name        = "PagoPA Resource Policy Reader"
#   scope       = data.azurerm_management_group.pagopa.id
#   description = "Read policy"

#   permissions {
#     actions = [
#     ]
#   }
# }
