# Copilot Instructions - eng-azure-governance

## 🎯 Repository Purpose

This repository contains all PagoPA Azure Policies and assignments for governance of Azure workloads. It handles:

- **Custom RBAC Roles**: Least privilege role definitions
- **Azure Policies**: Compliance and security controls by domain
- **Policy Initiatives (Sets)**: Grouped policies for easy assignment
- **Policy Assignments**: Deployment to Management Groups and Subscriptions

## 📁 Project Structure

```
eng-azure-governance/
├── src/
│   ├── 01_custom_roles/           # Custom RBAC role definitions
│   ├── 02_policy_*/               # Policy definitions by domain
│   │   ├── 02_policy_api_management/
│   │   ├── 02_policy_app_service/
│   │   ├── 02_policy_application_gateway/
│   │   ├── 02_policy_audit_logs/
│   │   ├── 02_policy_container_apps/
│   │   ├── 02_policy_cosmosdb/
│   │   ├── 02_policy_data_sovereignty/
│   │   ├── 02_policy_dns/
│   │   ├── 02_policy_event_hub/
│   │   ├── 02_policy_kubernetes/
│   │   ├── 02_policy_log_analytics/
│   │   ├── 02_policy_metrics_logs/
│   │   ├── 02_policy_networking/
│   │   ├── 02_policy_postgresql/
│   │   ├── 02_policy_redis/
│   │   ├── 02_policy_resource_lock/
│   │   ├── 02_policy_tags/
│   │   ├── 02_policy_virtual_machine/
│   │   └── 02_policy_virtual_machine_scale_set/
│   ├── 03_policy_set/             # Policy Initiatives (grouped policies)
│   ├── 04_policy_assignments/     # Assignments to MG/Subscriptions
│   └── scripts/                   # Utility scripts
├── .github/
│   └── workflows/                 # CI/CD pipelines
└── README.md
```

## 📋 Apply Order

Terraform must be applied in folder number order:

1. `01_custom_roles` - Create custom RBAC roles
2. `02_policy_*` - Create policy definitions
3. `03_policy_set` - Create policy initiatives
4. `04_policy_assignments` - Assign initiatives

## ✅ Mandatory Conventions

### Naming

- **Custom Roles**: Descriptive PascalCase (e.g., `AppServiceReader`)
- **Policies**: `pagopa-<domain>-<rule>` (e.g., `pagopa-storage-encryption`)
- **Policy Sets**: `pagopa-<domain>-<env>` (e.g., `pagopa-cosmosdb-prod`)
- **Assignments**: `<policy-set>-<scope>`

### Code

1. **Early Return**: Always use early return to reduce nesting
2. **Descriptive Logs**: Each log must explain the "why" with emoji prefix
   - ✅ Success
   - ❌ Error
   - ⚠️ Warning
   - 🔍 Debug/Info
   - 🚀 Operation start
   - 🏁 Operation end
3. **Simple Code**: Prioritize readability for human review
4. **Descriptive Comments**: Every script/workflow must have an explanatory header

### Terraform

- Use **tfenv** for version management (see `.terraform-version`)
- Backend: Azure Storage (`tfinforg` container)
- Run with `./terraform.sh plan|apply|destroy`
- Always run `terraform fmt` before committing
- Lock file must support multiple platforms

### Policy Definitions

- Follow Azure Policy structure
- Include clear descriptions
- Document parameters
- Test in non-production first

### Scripts

- **Bash**: Primarily `terraform.sh` wrapper
- **Header**: Always include purpose and usage

## 🚫 What NOT to Do

- ❌ Never skip apply order (must be sequential by folder number)
- ❌ Never hardcode subscription IDs in policies
- ❌ Never commit sensitive data
- ❌ Never bypass the PR review process
- ❌ Don't create overly restrictive policies without testing
- ❌ Don't assign policies to production without UAT testing

## 🎯 Design Principles

- **DDD (Domain-Driven Design)**: Organize policies by resource domain
- **Separation of Concerns**: Each folder = one policy domain
- **Idempotency**: Operations must be repeatable safely
- **Least Privilege**: Custom roles with minimal permissions
- **Environment Parity**: Consistent policies across dev/uat/prod

## 👥 Target Users

- **Cloud Engineering Team**: Repository maintainers
- **Security Team**: Policy review and compliance
- **Platform Teams**: Request policy exceptions

## 🔄 Preferred Workflow

1. Create feature branch from `main`
2. Make changes following apply order
3. Test with `./terraform.sh plan`
4. Open Pull Request
5. CI runs drift detection
6. Merge triggers deployment

## 🔍 Policy Evaluation

To force policy re-evaluation:

```bash
az account set -s MY-SUBSCRIPTION
az policy state trigger-scan --no-wait
# Or for specific resource group:
az policy state trigger-scan -g my-rg --no-wait
```
