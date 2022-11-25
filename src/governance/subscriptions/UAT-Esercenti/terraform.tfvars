env_short = "u"
prefix    = "cgnonboardingportal"


tags_subscription = {
  CostCenter   = "TS310 - PAGAMENTI & SERVIZI"
  Environment  = "UAT"
  Owner        = "IO"
  BusinessUnit = "IO"
  Renew        = "v1"
}

#
# 💰 BUDGET
#
action_group_budget_resource_group = "cgnonboardingportal-u-monitor-rg"
action_group_budget_name           = "cgnuerror"

budget_subscription_enabled = true
budget_subscription_resource_group          = "cgnonboardingportal-u-monitor-rg"
budget_subscription_amount     = 700
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
