# Project Purpose

## PUR — Purpose and scope

`eng-azure-governance` maintains PagoPA's Azure governance controls and the
repository knowledge that supports Azure lifecycle decisions. It covers four
areas with separate vocabularies, recorded in the [glossary map](../GLOSSARY-MAP.md)
and [ADR-0001](adr/0001-domain-layout.md):

- **Azure Governance**: custom roles, policy definitions, initiatives,
  assignments, and remediation for PagoPA Azure scopes.
- **Identity**: the repository's production workload identity and its Azure
  access grants.
- **Eng FinOps Platform Catalog**: the canonical mapping of Azure
  subscriptions to Eng FinOps platforms.
- **Azure Retirement Intelligence**: Azure retirement evidence collected and
  projected for committee review.

The Cloud Engineering team maintains the repository. The retirement committee
consumes the retirement artifacts.

Changes stay within the owning area, respect accepted decisions and domain
rules, and follow the [engineering principles](engineering-principles.md).

Evidence: [repository README](../README.md),
[architecture](architecture.md), [contribution guide](../CONTRIBUTING.md), and
the [retirement exporter README](../src/comitato/comitato_azure_retirements/README.md).
