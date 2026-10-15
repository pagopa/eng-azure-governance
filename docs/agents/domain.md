# Domain Docs

Before exploring, read the [documentation index](../README.md), the root
[glossary map](../../GLOSSARY-MAP.md), the glossary and rules for the current
area, and repository ADRs that affect it.

This repository uses the multi-context layout recorded by
[ADR-0001](../adr/0001-domain-layout.md), with the file names set by
[ADR-0002](../adr/0002-glossary-file-names.md):

- [Azure Governance](../domain/azure-governance/GLOSSARY.md) and its [rules](../domain/azure-governance/RULES.md).
- [Identity](../domain/identity/GLOSSARY.md) and its [rules](../domain/identity/RULES.md).
- [Eng FinOps Platform Catalog](../domain/eng-finops-platform-catalog/GLOSSARY.md) and its [rules](../domain/eng-finops-platform-catalog/RULES.md).
- [Azure Retirement Intelligence](../domain/azure-retirements/GLOSSARY.md) and its [rules](../domain/azure-retirements/RULES.md).
- [Cross-context](../domain/cross-context/GLOSSARY.md) for terms whose meaning differs between contexts.

`GLOSSARY.md` files contain definitions only. Relationships between contexts
live in the glossary map; rules live in `RULES.md`, and each rule names the
strategic item it serves.

Use glossary terms consistently and surface conflicts with accepted ADRs before
editing.
