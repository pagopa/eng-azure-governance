## Description

<!-- Describe the policy/custom role/initiative change and intended control. -->

## Change Type

- [ ] Custom RBAC role update
- [ ] Policy definition update
- [ ] Initiative/policy set update
- [ ] Policy assignment or remediation update
- [ ] Terraform/script automation update
- [ ] Documentation only
- [ ] Other

## Governance Impact

- Affected management groups/subscriptions:
- Policy effect (`audit`, `deny`, `modify`, other):
- Blast radius:
- Rollback strategy:

## Validation Evidence

- Terraform plan summary:
- Policy evaluation/testing summary:
- Additional validation details:

## Checklist

- [ ] Apply sequence impact (01 -> 02 -> 03 -> 04) was considered
- [ ] High-impact policy effects are explicitly documented
- [ ] `terraform fmt -recursive` and `terraform validate` executed
- [ ] Non-production validation performed before production scope
- [ ] No secrets or sensitive values included
