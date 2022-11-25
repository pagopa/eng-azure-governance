env_short               = "p"
prefix                  = "dvopau"
subscription_foundation = true

tags_subscription = {
  CostCenter   = "TS310 - PAGAMENTI & SERVIZI"
  Environment  = "PROD"
  Owner        = "DevOps team"
  BusinessUnit = "DevOps team"
  Renew        = "v1"
}

#
# 💰 BUDGET
#
action_group_budget_resource_group = "dvopau-p-monitor-rg"
action_group_budget_name           = "dvopauperror"

budget_subscription_enabled = true
budget_subscription_resource_group          = "dvopau-p-monitor-rg"
budget_subscription_amount     = 10
budget_subscription_time_grain = "Monthly"

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

