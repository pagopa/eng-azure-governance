---
name: antigravity-api-design-principles
description: REST and GraphQL API design principles for resource modeling, contracts, pagination, versioning, errors, and developer experience. Use when designing or reviewing API interfaces, specifications, or public integration contracts.
risk: safe
source: community
date_added: '2026-03-29'
---

# API Design Principles

Use this skill for API contract quality, not framework-specific implementation details.

## Workflow

1. Identify consumers and usage patterns.
2. Choose the interface style that fits the product and team constraints.
3. Define consistent resource or type models.
4. Specify pagination, errors, authentication, and versioning early.
5. Validate the contract with realistic examples before implementation.

## Design Priorities

- Clear nouns and stable resource boundaries
- Predictable filtering, sorting, and pagination
- Error models that are actionable for clients
- Backward compatibility discipline
- Documentation that matches actual request and response behavior

## Guardrails

- Do not expose storage shape as API shape by default.
- Do not mix transport decisions and business semantics carelessly.
- Avoid versioning churn caused by weak initial modeling.
- Prefer consistency over one-off endpoint cleverness.
