# Glossary Map

## Contexts

- [Azure Governance](docs/domain/azure-governance/GLOSSARY.md): policy controls, custom roles, initiatives, assignments, and remediation
- [Identity](docs/domain/identity/GLOSSARY.md): the repository's production workload identity, its federation, and its Azure access grants
- [Eng FinOps Platform Catalog](docs/domain/eng-finops-platform-catalog/GLOSSARY.md): the versioned mapping of Azure subscriptions to Eng FinOps platforms
- [Azure Retirement Intelligence](docs/domain/azure-retirements/GLOSSARY.md): Azure retirement evidence collected and projected for committee review
- [Cross-context](docs/domain/cross-context/GLOSSARY.md): terms whose meaning differs between contexts

## Relationships

- **Azure Governance → Identity**: Identity grants the production identity custom roles that Azure Governance defines, referenced by stable role name.
- **Eng FinOps Platform Catalog → Azure Retirement Intelligence**: the retirement runtimes read active subscription-to-platform mappings from the canonical catalog.

Component paths, Terraform roots, and state boundaries are owned by [architecture](docs/architecture.md).
