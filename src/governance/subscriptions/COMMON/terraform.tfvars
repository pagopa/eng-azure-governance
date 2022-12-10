env_short               = "p"
env                     = "prod"
prefix                  = "common"
subscription_foundation = true

tags_subscription = {
  CostCenter   = "TS310 - PAGAMENTI & SERVIZI"
  Environment  = "PROD"
  Owner        = "DevOps"
  BusinessUnit = "DevOps Team"
  Renew        = "v1"
}

#
# 💰 BUDGET
#
action_group_budget_resource_group = "common-p-monitor-rg"
action_group_budget_name           = "commonperror"

budget_subscription_enabled        = true
budget_subscription_resource_group = "common-p-monitor-rg"
budget_subscription_amount         = 240
budget_subscription_time_grain     = "Monthly"

budget_subscription_notifications = [
  {
    enabled        = true
    threshold      = 80
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Actual"
  },
  {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Actual"
  },
  {
    enabled        = true
    threshold      = 110
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Actual"
  },
  {
    enabled        = true
    threshold      = 100
    operator       = "GreaterThanOrEqualTo"
    threshold_type = "Forecasted"
  },
]
