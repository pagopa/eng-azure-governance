# Engineering Principles

These principles apply across change cycles. The repository owner accepted
them on 2026-10-14 from the evidence cited under each principle.

## PRI-01 — Least privilege

Scope roles, policies, and grants to the narrowest effective target and
capability.

Evidence: [security baseline](../.github/security-baseline.md),
[GOV-002](domain/azure-governance/RULES.md), and the custom-role guidance in
[CONTRIBUTING.md](../CONTRIBUTING.md).

## PRI-02 — Federated, short-lived credentials

Authenticate automation with federated, short-lived credentials instead of
long-lived static secrets.

Evidence: [security baseline](../.github/security-baseline.md) and the
federated identity credential in `.identity/02_identity_prod.tf`.

## PRI-03 — Evidence over inference

Derive published claims from authoritative sources; never infer impact,
mappings, or values that the source does not state.

Evidence: [RET-002](domain/azure-retirements/RULES.md), the
[retirement exporter README](../src/comitato/comitato_azure_retirements/README.md),
and the [v2 retirement README](../src/comitato/comitato_azure_retirements_v2/README.md).

## PRI-04 — Visible degradation

Make partial or failed results explicit; never present them as a clean
outcome.

Evidence: [RET-001 and RET-005](domain/azure-retirements/RULES.md) and the
publication behavior in the
[v2 retirement README](../src/comitato/comitato_azure_retirements_v2/README.md).

## PRI-05 — Non-mutating validation

Local and pull-request validation never reaches or changes remote state.

Evidence: [GOV-004](domain/azure-governance/RULES.md), `.pre-commit-config.yaml`,
and `.github/workflows/_pre-commit.yml`.
