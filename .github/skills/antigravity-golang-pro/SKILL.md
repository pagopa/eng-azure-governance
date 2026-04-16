---
name: antigravity-golang-pro
description: Modern Go development for services, CLIs, concurrency patterns, profiling, and production readiness. Use when building or reviewing Go code, Go architecture, goroutine coordination, or Go performance work.
risk: unknown
source: community
date_added: '2026-03-29'
---

# Golang Pro

Use this skill when the repository or task is Go-specific and needs more than syntax help.

## Core Use Cases

- Go service or CLI design
- Concurrency and goroutine coordination
- Profiling and performance analysis
- Production readiness and operational hardening

## Workflow

1. Confirm Go version and module/tooling constraints.
2. Choose the simplest concurrency model that fits the workload.
3. Prefer standard-library patterns first.
4. Add tests and profiling before claiming an optimization.

## Guardrails

- Prefer composition over framework-heavy abstractions.
- Treat context propagation and cancellation as design requirements.
- Avoid clever concurrency when a worker pool or pipeline is enough.
- Measure CPU and memory behavior before tuning.
