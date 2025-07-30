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
    "PROD-P4PA",
    "PROD-TRIAL",
    "PROD-ARC",
    "PROD-GRC",
    "PROD-PDA-BACKUP",
    "PROD-ICT",
    "PROD-CRM",
    "ORG",
    "ORG-PCI",
    "Common",
    "DevOpsAutomation",
    "PROD-DEVEX",
    "PROD-PLATFORM-SM",
    "GitHub",
    "PROD-PAY-MONITORING",
  ]
}

module "prod_assignments" {
  source = "./modules/prod"

  for_each = toset(local.prod_subscriptions)

  subscription   = [for s in data.azurerm_subscriptions.available.subscriptions : s if s.display_name == each.value][0]
  location       = var.location
  policy_set_ids = data.terraform_remote_state.policy_set.outputs
}

resource "azurerm_resource_policy_exemption" "pioauditlogs_fims_waiver" {
  name                 = "pioauditlogs-fims-waiver"
  exemption_category   = "Waiver"
  description          = "fims-rp is an example app and does not require audit logs to be enabled"
  resource_id          = "/subscriptions/ec285037-c673-4f58-b594-d7c480da4e8b/resourcegroups/io-p-weu-fims-rg-01/providers/microsoft.web/sites/io-p-weu-fims-rp-example-app-02"
  policy_assignment_id = "/subscriptions/ec285037-c673-4f58-b594-d7c480da4e8b/providers/microsoft.authorization/policyassignments/pioauditlogs"
  policy_definition_reference_ids = [
    "app_service_workspaceid",
    "app_service_storageid_westeurope",
    "app_service_storageid_northeurope",
    "app_service_storageid_italynorth",
  ]
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
