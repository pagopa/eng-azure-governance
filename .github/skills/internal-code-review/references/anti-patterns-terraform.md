# Terraform Anti-Patterns

Reference: `instructions/internal-terraform.instructions.md`

## Critical
| ID | Anti-pattern | Why |
|---|---|---|
| TF-C01 | Hardcoded secrets, access keys, or passwords in `.tf` files | Credential exposure |
| TF-C02 | Overly broad IAM policy with `"Action": "*"` or `"Resource": "*"` | Excessive privilege |
| TF-C03 | Backend configuration with no state locking | Concurrent state corruption |

## Major
| ID | Anti-pattern | Why |
|---|---|---|
| TF-M01 | `count` used where `for_each` with logical keys is appropriate | Index-based drift risk |
| TF-M02 | Missing `description` on variables | Undocumented interface |
| TF-M03 | Missing `type` constraint on variables | Unvalidated input |
| TF-M04 | Hardcoded resource IDs, ARNs, or subscription IDs | Non-portable, environment-coupled |
| TF-M05 | Missing `prevent_destroy` on critical production resources | Accidental deletion risk |
| TF-M06 | Provider version not pinned in `required_providers` | Non-deterministic plans |
| TF-M07 | `ignore_changes` without documented rationale | Hidden drift |
| TF-M08 | Missing tags on taggable resources | Governance and cost tracking gap |

## Minor
| ID | Anti-pattern | Why |
|---|---|---|
| TF-m01 | Unused variables or outputs | Dead code |
| TF-m02 | Missing `description` on outputs | Undocumented contract |
| TF-m03 | Missing `terraform fmt` (inconsistent formatting) | Style consistency |
| TF-m04 | Inline policy JSON instead of `aws_iam_policy_document` data source | Readability and validation |
| TF-m05 | Missing `create_before_destroy` on replacement-sensitive resources | Downtime risk |
| TF-m06 | Locals not grouped by domain | Organizational clarity |

## Nit
| ID | Anti-pattern | Why |
|---|---|---|
| TF-N01 | Resource name not in `snake_case` | Naming convention |
| TF-N02 | Inconsistent ordering of block arguments | Readability |
| TF-N03 | Empty `default = ""` instead of `default = null` for optional strings | Semantic clarity |
| TF-N04 | Comments with `//` instead of `#` | HCL convention |
| TF-N05 | Missing blank line between resource blocks | Visual structure |

## Good vs bad examples

```hcl
# BAD (TF-M01): count with conditional
resource "aws_iam_role" "lambda" {
  count = var.enable_lambda ? 1 : 0
  name  = "lambda-role-${count.index}"
}

# GOOD: for_each with logical key
resource "aws_iam_role" "lambda" {
  for_each = var.enable_lambda ? toset(["main"]) : toset([])
  name     = "lambda-role-${each.key}"
}
```

```hcl
# BAD (TF-M02, TF-M03): no description, no type
variable "env" {}

# GOOD: typed, described, validated
variable "env" {
  description = "Deployment environment name."
  type        = string

  validation {
    condition     = contains(["dev", "uat", "prod"], var.env)
    error_message = "env must be one of: dev, uat, prod."
  }
}
```
