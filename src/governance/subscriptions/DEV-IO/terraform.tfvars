env_short = "d"
prefix    = "io"

tags_subscription = {
  CostCenter   = "TS310 - PAGAMENTI & SERVIZI"
  Environment  = "DEV"
  Owner        = "IO"
  BusinessUnit = "IO"
  Renew        = "v1"
}

#
# 💰 BUDGET
#
action_group_budget_resource_group = "io-d-monitoring"
action_group_budget_name           = "ioderror"

budget_subscription_enabled        = true
budget_subscription_resource_group = "io-d-monitoring"
budget_subscription_amount         = 500
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
