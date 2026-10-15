locals {
  subscription_name = lower(var.subscription.display_name)
  prefix            = replace(replace(local.subscription_name, "-", ""), "/^dev/", "d")
}
