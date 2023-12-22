locals {
  prod_subscriptions = [
    "PROD-CSTAR",
    "PROD-Esercenti",
    "PROD-FATTURAZIONE",
    "PROD-IO",
    "PROD-mil",
    "Prod-Sec",
    "PROD-SITECORP",
    "PROD-SelfCare",
    "PROD-pagoPA",
    "PROD-PCI",
    "ORG",
    "Common",
    "DevOpsAutomation",
  ]
}

module "prod_assignments" {
  source = "./modules/prod"

  for_each = toset(local.prod_subscriptions)

  subscription   = [for s in data.azurerm_subscriptions.available.subscriptions : s if s.display_name == each.value][0]
  location       = var.location
  policy_set_ids = data.terraform_remote_state.policy_set.outputs
}