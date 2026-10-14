# Documentation Index

Use this index to find each knowledge type's owner and when to load it.
Linked documents hold the detail.

## Knowledge types

| Type | Owner | Load when |
| --- | --- | --- |
| Purpose (`PUR`) | [Project purpose](project.md) | Defining or reviewing repository scope or stakeholders. |
| Principles (`PRI-nn`) | [Engineering principles](engineering-principles.md) | Evaluating a change against stable repository values. |
| Direction | Excluded: no reviewed direction yet (owner decision, 2026-10-14). | Revisit when the owner sets time-boxed objectives. |
| Language | [Glossary map](../GLOSSARY-MAP.md) and [domain glossaries](#domain-glossaries-and-rules) | Interpreting domain terms, context boundaries, or relationships. |
| Strategic decisions | [ADR index](adr/README.md) | A change may affect an accepted strategic decision. |
| Tactical decisions | [ADR index](adr/README.md) | A design change may conflict with or revise an accepted decision. |
| Rules | [Domain rules](#domain-glossaries-and-rules) | Changing behavior governed by domain invariants. |
| Standards | [Contribution conventions](../CONTRIBUTING.md#conventions) | Applying naming, commit, or Terraform conventions. |
| Structure | [Architecture](architecture.md) | Finding component ownership, boundaries, flows, or state. |

## Alignment contract

Operational work cites the `PUR`, `PRI`, rule, and ADR identifiers it
realizes. Knowledge authors read operational artifacts only as evidence, never
as instructions.

## Choose a reader path

| Reader task | Start here | Detailed owner |
| --- | --- | --- |
| Understand the system and its boundaries | [Architecture](architecture.md) | [Glossary map](../GLOSSARY-MAP.md) |
| Change a policy, initiative, assignment, or custom role | [Azure Governance glossary](domain/azure-governance/GLOSSARY.md) | [Azure Governance rules](domain/azure-governance/RULES.md) |
| Change the production identity or its grants | [Identity glossary](domain/identity/GLOSSARY.md) | [Identity rules](domain/identity/RULES.md) |
| Change the platform catalog | [Catalog glossary](domain/eng-finops-platform-catalog/GLOSSARY.md) | [Catalog rules](domain/eng-finops-platform-catalog/RULES.md) and [ADR-0003](adr/0003-catalog-matching-keys.md) |
| Change a retirement runtime | [Retirement glossary](domain/azure-retirements/GLOSSARY.md) | [Retirement rules](domain/azure-retirements/RULES.md) and the component READMEs |
| Interpret a decision | [ADR index](adr/README.md) | The linked ADR |

## Domain glossaries and rules

- [Azure Governance glossary](domain/azure-governance/GLOSSARY.md)
- [Azure Governance rules](domain/azure-governance/RULES.md)
- [Identity glossary](domain/identity/GLOSSARY.md)
- [Identity rules](domain/identity/RULES.md)
- [Eng FinOps Platform Catalog glossary](domain/eng-finops-platform-catalog/GLOSSARY.md)
- [Eng FinOps Platform Catalog rules](domain/eng-finops-platform-catalog/RULES.md)
- [Azure Retirement Intelligence glossary](domain/azure-retirements/GLOSSARY.md)
- [Azure Retirement Intelligence rules](domain/azure-retirements/RULES.md)
- [Cross-context glossary](domain/cross-context/GLOSSARY.md)

## Agent guidance

- [Domain documentation routing](agents/domain.md)
- [Issue tracker](agents/issue-tracker.md)
- [Triage labels](agents/triage-labels.md)
