metadata_category_name = "Custom PagoPA"
policy_type            = "Custom"
location               = "westeurope"

subscription_blacklist = [
  "Microsoft Azure Enterprise",
  "MDASH-Evaluation",
  "COPILOT-IO-APP",
  "COPILOT-IO-CARABINIERI",
  "COPILOT-IO-WALLET",
  "COPILOT-IO-CGN",
  "COPILOT-TECHNOLOGY-CLOUD-STRATEGY",
]

subscription_environment_overrides = {
  DevOpsLab                = "dev"
  ORG                      = "prod"
  Common                   = "prod"
  DevOpsAutomation         = "prod"
  GitHub                   = "prod"
  PDA-Migration-PostgreSQL = "prod"
}
