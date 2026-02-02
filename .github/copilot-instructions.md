# Copilot Instructions - eng-azure-governance

## 🎯 Repository Purpose
Central repository for PagoPA **Azure Policies**, Initiatives (Sets), Assignments, and Custom RBAC roles.

## 📁 Key Project Structure
- `src/01_custom_roles/`: Custom RBAC role definitions.
- `src/02_policy_*/`: Policy definitions grouped by domain (networking, db, storage, etc.).
- `src/03_policy_set/`: Policy Initiatives (aggregating multiple policies).
- `src/04_policy_assignments/`: Assignments to Management Groups or Subscriptions.

## 🛠️ Critical Workflows
1. **Apply Order**: Folders MUST be applied in numeric order: `01` -> `02` -> `03` -> `04`.
2. **Execution**: Use `./terraform.sh plan|apply|destroy` from the root or target folder.
3. **Re-evaluation**: Force Azure Policy scan: `az policy state trigger-scan --no-wait`.

## ✅ Mandatory Conventions
- **Naming**:
    - Roles: PascalCase (e.g., `AppServiceReader`).
    - Policies: `pagopa-<domain>-<rule>` (e.g., `pagopa-storage-encryption`).
    - Sets: `pagopa-<domain>-<env>`.
- **Terraform**: Use `tfenv`, Azure Storage backend (`tfinforg`), run `terraform fmt`.
- **Logging**: Use emoji prefixes (✅ Success, ❌ Error, ⚠️ Warning, 🔍 Info, 🚀 Start).

## 🚫 What NOT to Do
- ❌ Skip the numeric apply order.
- ❌ Hardcode subscription IDs in policies.
- ❌ Assign new policies directly to production without UAT testing.

## 📚 Reference
See [Azure Policy Concept Structure](https://docs.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure) for guidance.

