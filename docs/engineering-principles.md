# Engineering Principles

These principles apply across change cycles. The repository owner accepted
them on 2026-10-14 from the evidence cited under each principle.

## PRI-01 — Least privilege

Scope roles, policies, and grants to the narrowest effective target and
capability.

Evidence: [custom RBAC security guidance](../SECURITY.md#custom-rbac-roles),
[GOV-002](domain/azure-governance/RULES.md), and the custom-role guidance in
[CONTRIBUTING.md](../CONTRIBUTING.md).

## PRI-02 — Federated, short-lived credentials

Authenticate automation with federated, short-lived credentials instead of
long-lived static secrets.

Evidence: the federated identity credential in
[the production identity configuration](../.identity/02_identity_prod.tf).

## PRI-03 — Evidence over inference

Derive published claims from authoritative sources; never infer impact,
mappings, or values that the source does not state.

Evidence: [RET-002](domain/azure-retirements/RULES.md), the
[v2 retirement README](../src/comitato/comitato_azure_retirements_v2/README.md).

## PRI-04 — Visible degradation

Make partial or failed results explicit; never present them as a clean
outcome.

Evidence: [RET-001](domain/azure-retirements/RULES.md) and the
publication behavior in the
[v2 retirement README](../src/comitato/comitato_azure_retirements_v2/README.md).

## PRI-05 — Non-mutating validation

Offline local checks and pull-request pre-commit validation never reach or
change remote state. Terraform plans with Azure access are separate operational
checks, not part of offline validation.

Evidence: [GOV-004](domain/azure-governance/RULES.md), `.pre-commit-config.yaml`,
`.github/workflows/_pre-commit.yml`, and the operational plan guidance in
[architecture](architecture.md#10-testing-and-validation).
