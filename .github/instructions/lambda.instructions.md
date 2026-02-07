---
applyTo: "**/*lambda*.tf,**/*lambda*.py,**/*lambda*.js,**/*lambda*.ts"
---

# Lambda Instructions

## Design
- Keep handlers small and explicit.
- Validate input early.
- Prefer pure helpers for business logic.

## Operations
- Define timeout/memory explicitly.
- Log meaningful lifecycle events in English.
- Avoid embedding secrets; use environment/secret stores.

## Testing
- Keep unit tests isolated from cloud runtime.
- Mock external dependencies and network calls.
