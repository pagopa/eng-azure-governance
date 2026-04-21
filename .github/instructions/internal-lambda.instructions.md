---
description: Lambda implementation rules for explicit handlers, input validation, and reusable business logic.
applyTo: "**/*lambda*.tf,**/*lambda*.py,**/*lambda*.js,**/*lambda*.ts"
---

# Lambda Instructions

## Design

- Treat this instruction as the repository-owned baseline for Lambda or serverless implementation guidance in this catalog; keep runtime-specific detail in the paired Python or Node.js instructions.
- Prefer one focused function per trigger or operation; avoid monolithic handlers that mix unrelated flows.
- Keep handlers small and explicit; move business logic to pure helpers.
- Validate input early and return structured errors.
- Keep handler signature and event parsing explicit for the target runtime and event source.
- When Lambda fronts an HTTP endpoint, normalize body/path/query parsing and return transport-compatible JSON responses with explicit headers.
- Configure API routes, methods, and CORS deliberately instead of relying on implicit defaults.
- For queue-driven handlers, process records independently and make retry behavior explicit.

## Runtime and performance

- Measure INIT duration separately from invocation latency before optimizing cold-start issues.
- Minimize cold-start overhead by avoiding heavy imports in the global scope.
- Keep dependencies small and prefer modular SDK clients over broad package imports.
- Configure timeout and memory explicitly based on workload profile.
- Reuse initialized clients safely across invocations when runtime allows it.
- Avoid unnecessary VPC attachment; if a VPC is required, validate DNS, egress, and connection behavior under cold start.

## Packaging and deployment

- Keep deployment artifact deterministic and reproducible.
- Keep each function package focused on one responsibility instead of shipping a large shared monolith.
- Use layers only for shared dependencies with clear versioning.
- Keep environment variables configuration-only; secrets must come from managed secret stores.
- For queue-triggered Lambdas, pair the source queue with explicit DLQ/redrive configuration and a visibility timeout sized relative to the function timeout.
- When the event source supports partial batch failure reporting, enable it and return only failed record identifiers for retry.

## Runtime cross-references

- For AWS-specific Lambda implementation patterns, load `.github/skills/internal-aws-serverless/SKILL.md` when the task needs API Gateway, SQS, packaging, or cold-start guidance.
- For Python Lambdas, also follow `.github/instructions/internal-python.instructions.md`.
- For JavaScript or TypeScript Lambdas, also follow `.github/instructions/internal-nodejs.instructions.md`.

## Observability

- Log key lifecycle events in English with stable fields for filtering.
- Prefer structured logs for production workloads.
- Include request or correlation identifiers in error logs when the runtime provides them.
- Emit enough context for correlation without leaking sensitive values.

## Testing

- Keep unit tests isolated from cloud runtime.
- Mock external dependencies and network calls.
