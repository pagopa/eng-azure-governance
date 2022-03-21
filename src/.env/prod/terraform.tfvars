# general
location               = "northeurope"
metadata_category_name = "PagoPA"

tags_subscription_to_inherith = [
  "CreatedBy",
  "Environment",
  "Owner",
  "Source",
  "CostCenter",
  "BusinessUnit",
]

#
# Allowed SKUs
#
devops_vm_skus_allowed = [
  "Standard_B12ms",
  "Standard_B16ms",
  "Standard_B1ls",
  "Standard_B1ms",
  "Standard_B1s",
  "Standard_B20ms",
  "Standard_B2ms",
  "Standard_B2s",
  "Standard_B4ms",
  "Standard_B8ms",
  "Standard_D4s_v5",
  "Standard_D2s_v5",
]

dev_vm_skus_allowed = [
  "Standard_B12ms",
  "Standard_B16ms",
  "Standard_B1ls",
  "Standard_B1ms",
  "Standard_B1s",
  "Standard_B20ms",
  "Standard_B2ms",
  "Standard_B2s",
  "Standard_B4ms",
  "Standard_B8ms",
  "Standard_D4s_v5",
  "Standard_D2s_v5",
]

uat_vm_skus_allowed = [
  "Standard_D4s_v5",
  "Standard_D2s_v5",
]

prod_vm_skus_allowed = [
  "Standard_D4s_v5",
  "Standard_D2s_v5",
]

#
# Allowed Locations
#

devops_allowed_locations = [
  "global",
  "northeurope",
  "westeurope",
  "westus2"
]

dev_allowed_locations = [
  "global",
  "northeurope",
  "westeurope",
  "westus2"
]

uat_allowed_locations = [
  "global",
  "northeurope",
  "westeurope",
]

prod_allowed_locations = [
  "global",
  "northeurope",
  "westeurope",
]

certificate_authority_cn = "C=US, O=Let's Encrypt, CN=R3"
