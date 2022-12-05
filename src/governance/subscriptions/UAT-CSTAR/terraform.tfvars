env_short = "u"
prefix    = "cstar"

tags_subscription = {
  CostCenter   = "TS310 - PAGAMENTI & SERVIZI"
  Environment  = "UAT"
  Owner        = "CSTAR"
  BusinessUnit = "CentroStella"
  Renew        = "v1"
}

#
# 💰 BUDGET
#
action_group_budget_resource_group = "cstar-u-monitor-rg"
action_group_budget_name           = "cstaruerror"

budget_subscription_enabled        = true
budget_subscription_resource_group = "cstar-u-monitor-rg"
budget_subscription_amount         = 3500
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
