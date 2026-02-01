# Code Review Instructions - eng-azure-governance

## 🎯 Review Focus

### Custom Roles (`01_custom_roles/`)

- [ ] Role name is descriptive
- [ ] Permissions follow least privilege
- [ ] No unnecessary wildcards in actions
- [ ] Scope is appropriate

### Policy Definitions (`02_policy_*/`)

- [ ] Policy name follows `pagopa-*` convention
- [ ] Description is clear and helpful
- [ ] Parameters are documented
- [ ] Effect is appropriate (Audit vs Deny)
- [ ] Conditions are correct

### Policy Initiatives (`03_policy_set/`)

- [ ] Initiative groups related policies
- [ ] Parameters are properly mapped
- [ ] Environment-specific configurations correct
- [ ] Naming follows convention

### Policy Assignments (`04_policy_assignments/`)

- [ ] Scope is correct (MG/Subscription)
- [ ] Parameters are properly set
- [ ] Exemptions are documented
- [ ] Not bypassing security controls

### Terraform Files

- [ ] Proper formatting (`terraform fmt`)
- [ ] Variables have descriptions
- [ ] No hardcoded IDs
- [ ] Backend configuration correct

## ⚠️ Red Flags

- 🚨 **Immediate rejection**:
  - Hardcoded credentials or secrets
  - Overly permissive custom roles
  - Policies that could break production
  - Skipping apply order

- ⚠️ **Request changes**:
  - Unformatted Terraform code
  - Missing policy descriptions
  - Unclear naming
  - Missing documentation

## ✅ Approve if

- All automated checks pass
- Terraform plan shows expected changes
- Apply order is respected
- Policies tested in non-production
- Naming conventions followed
- Security impact assessed
