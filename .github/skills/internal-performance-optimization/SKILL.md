---
name: internal-performance-optimization
description: Use when performance is the primary problem, such as profiling slowness, reducing latency, improving throughput, or preventing regressions across frontend, backend, or database layers.
---

# Internal Performance Optimization

Use this skill when performance is the primary constraint. Start from evidence, not intuition.

## When to use

- The user already has profiling evidence, benchmark data, query plans, or trace data pointing to a real bottleneck.
- The user has an explicit performance goal such as lower latency, higher throughput, or regression prevention that can be measured.

## When not to use

- The request is generic debugging with no evidence that performance is the dominant problem.
- The request is network-path specific and the main need is topology, connectivity, or transport tuning rather than application or database behavior.

## Workflow

1. Measure the problem.
2. Locate the hottest path.
3. Remove wasted work.
4. Validate with before/after evidence.
5. Protect the gain with tests, benchmarks, or budgets.

## Core Rules

- Do not optimize blind.
- Fix the dominant bottleneck first.
- Prefer simpler code paths before micro-optimizations.
- Avoid broad caching until query shape, render flow, or algorithm choice is understood.
- Treat database, network, and serialization costs as first-class suspects.

## Frontend Checks

- Re-render frequency
- Bundle size and lazy loading
- DOM churn and expensive layout work
- Image, font, and asset weight
- Request waterfalls and client caching

## Backend Checks

- N+1 patterns
- Avoidable I/O round-trips
- Unbounded concurrency
- Slow serialization or parsing
- Inefficient algorithms or data structures

## Database Checks

- Execution plan shape and row-estimate mismatches
- Missing or badly ordered indexes
- Functions on indexed columns in predicates
- Over-fetching
- Offset pagination on large tables
- Repeated aggregations that should be consolidated

## PostgreSQL-Specific Checks

- `EXPLAIN ANALYZE` and `pg_stat_statements`
- JSONB with GIN indexes only when the workload truly benefits
- Partial and expression indexes for selective predicates
- Full-text search when text filtering outgrows `LIKE`
- Extension choices only when they are explicit, justified, and operationally supportable

## Memory and CPU

- High allocation churn
- Duplicate object creation
- Work that should be streamed or batched
- Work happening on the critical path that can move off it

## Regression Prevention

After a fix, add at least one of:

- Benchmark or load-test coverage
- Performance budget
- Query-plan validation
- Monitoring or alert threshold

## Cross-references

- Use `obra-systematic-debugging` when the first problem is still root-cause isolation rather than a confirmed performance bottleneck.
- Use `antigravity-network-engineer` when latency, packet flow, DNS, load-balancer behavior, or network topology is the primary bottleneck.

## Anti-Patterns

- Premature optimization before profiling
- Using `SELECT *` in hot paths
- Adding cache layers to hide broken query shapes
- Using JSONB as a catch-all when relational modeling is clearer
- Adopting PostgreSQL extensions or indexes without plan evidence and write-cost awareness
- Optimizing cold code because it is easy to touch
- Claiming performance gains without measurements
