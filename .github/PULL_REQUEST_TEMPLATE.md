<!-- markdownlint-disable-file MD041 -->
<!-- PR title format: <type>(<scope>): <summary> -->
<!-- Examples: feat(terraform): add new SCP policy -->
<!--           fix(scripts): correct JSON validation logic -->

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
- Policy exemption impact:
- Rollback strategy:

## Testing Instructions

<!-- Step-by-step instructions for reviewers to validate changes -->
1.
2.

## Validation Evidence

- Terraform plan summary:
- Policy evaluation/testing summary:
- Additional validation details:

## Breaking Changes

- [ ] This PR contains breaking changes
<!-- If checked, describe what breaks and migration path -->

## Checklist

- [ ] Apply sequence impact (01 -> 02 -> 03 -> 04) was considered
- [ ] High-impact policy effects are explicitly documented
- [ ] `terraform fmt -recursive` and `terraform validate` executed
- [ ] Non-production validation performed before production scope
- [ ] No secrets or sensitive values included
