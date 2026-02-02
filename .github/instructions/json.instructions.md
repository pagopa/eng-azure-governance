---
applyTo: "**/*.json"
---

# JSON Files Instructions

## General Rules

- Use 2-space indentation
- No trailing commas
- UTF-8 encoding
- LF line endings

## Policy Rules (in Terraform)

When using `jsonencode()` for policy rules:

```hcl
policy_rule = jsonencode({
  if = {
    allOf = [
      {
        field  = "type"
        equals = "Microsoft.Storage/storageAccounts"
      },
      {
        field    = "Microsoft.Storage/storageAccounts/encryption.services.blob.enabled"
        notEquals = "true"
      }
    ]
  }
  then = {
    effect = "Deny"
  }
})
```

## Common Policy Conditions

### Field Conditions

```json
{
  "field": "fieldName",
  "equals": "value"
}
```

### Logical Operators

- `allOf`: All conditions must be true (AND)
- `anyOf`: Any condition must be true (OR)
- `not`: Negation

### Effects

| Effect | Description |
|--------|-------------|
| `Deny` | Prevent resource creation/modification |
| `Audit` | Log non-compliant resources |
| `AuditIfNotExists` | Audit if related resource missing |
| `DeployIfNotExists` | Deploy if related resource missing |
| `Modify` | Add/update/remove properties |
