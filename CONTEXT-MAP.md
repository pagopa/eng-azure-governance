# Context Map

This repository contains four knowledge domains with separate vocabularies, state, or execution lifecycles.

## Contexts

- [Azure Governance](./docs/domain/azure-governance/CONTEXT.md) - defines policy controls, custom roles, initiatives, assignments, and remediation.
- [Identity](./docs/domain/identity/CONTEXT.md) - establishes the repository's production workload identity, federation, and Azure access grants.
- [Eng FinOps Platform Catalog](./docs/domain/eng-finops-platform-catalog/CONTEXT.md) - maps Azure subscriptions to Eng FinOps platforms under a versioned schema and [catalog rules](./docs/domain/eng-finops-platform-catalog/RULES.md).
- [Azure Retirement Intelligence](./docs/domain/azure-retirements/CONTEXT.md) - collects and projects Azure retirement evidence for committee review.

## Relationships

- **Azure Governance -> Identity**: the Identity root grants the production identity two custom roles defined by the governance role stage, referenced by stable role name.
- **Eng FinOps Platform Catalog -> Azure Retirement Intelligence**: the retirement runtime loads active subscription-to-platform mappings from the canonical catalog.
- No other domain-to-domain data or control dependency is evidenced. In particular, checked-in files do not bind the Identity root's outputs to the GitHub environment secrets used by governance workflows.

The repository-level component relationships and external boundaries are recorded in [docs/architecture.md](./docs/architecture.md).
