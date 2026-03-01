---
description: Lambda implementation rules for explicit handlers, input validation, and reusable business logic.
applyTo: "**/*lambda*.tf,**/*lambda*.py,**/*lambda*.js,**/*lambda*.ts"
---

# Lambda Instructions

## Design
- Keep handlers small and explicit; move business logic to pure helpers.
- Validate input early and return structured errors.
- Keep handler signature and event parsing explicit for the target runtime.

## Runtime and performance
- Minimize cold-start overhead by avoiding heavy imports in the global scope.
- Configure timeout and memory explicitly based on workload profile.
- Reuse initialized clients safely across invocations when runtime allows it.

## Packaging and deployment
- Keep deployment artifact deterministic and reproducible.
- Use layers only for shared dependencies with clear versioning.
- Keep environment variables configuration-only; secrets must come from managed secret stores.

## Observability
- Log key lifecycle events in English with stable fields for filtering.
- Prefer structured logs for production workloads.
- Emit enough context for correlation without leaking sensitive values.

## Testing
- Keep unit tests isolated from cloud runtime.
- Mock external dependencies and network calls.
