module "prod_assignments" {
  source = "./modules/prod"

  for_each = local.subscriptions_by_environment.prod

  subscription   = each.value
  location       = var.location
  policy_set_ids = local.policy_set_ids
}

resource "azurerm_resource_policy_exemption" "pictresourcelock_ip_waiver" {
  name                 = "pictresourcelock-ip-waiver"
  exemption_category   = "Waiver"
  description          = "Error to enable lock on this resource"
  resource_id          = "/subscriptions/f4b92052-083f-493c-b765-6d6a28eb809c/resourceGroups/ME_ict-p-github-runner-cae_ict-p-github-runner-rg_italynorth/providers/Microsoft.Network/publicIPAddresses/capp-svc-lb-ip"
  policy_assignment_id = "/subscriptions/f4b92052-083f-493c-b765-6d6a28eb809c/providers/microsoft.authorization/policyassignments/pictresourcelock"
  policy_definition_reference_ids = [
    "10624036959092254356", # Public IP Address resource lock policy definition ID
  ]
}
