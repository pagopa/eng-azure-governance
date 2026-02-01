# AGENTS.md - eng-azure-governance

This file is for **OpenAI Codex CLI** and other AI agents.

## 📚 Main Instructions

👉 **[.github/copilot-instructions.md](.github/copilot-instructions.md)**

## 📂 Configuration Files

| File | Purpose |
|------|---------|
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | Global Copilot instructions |
| [.github/copilot-code-review-instructions.md](.github/copilot-code-review-instructions.md) | Code review guidelines |
| [.github/copilot-commit-message-instructions.md](.github/copilot-commit-message-instructions.md) | Commit message format |
| [.github/instructions/terraform.instructions.md](.github/instructions/terraform.instructions.md) | Terraform conventions |
| [.github/instructions/json.instructions.md](.github/instructions/json.instructions.md) | JSON/Policy conventions |
| [.github/instructions/scripts.instructions.md](.github/instructions/scripts.instructions.md) | Script conventions |

## 🎯 Available Prompts

| Prompt | Description |
|--------|-------------|
| [create-policy.prompt.md](.github/prompts/create-policy.prompt.md) | Create Azure Policy definition |
| [create-initiative.prompt.md](.github/prompts/create-initiative.prompt.md) | Create Policy Initiative |
| [create-custom-role.prompt.md](.github/prompts/create-custom-role.prompt.md) | Create custom RBAC role |

## ⚡ Quick Reference

### Apply Order (IMPORTANT!)

```
1. src/01_custom_roles/       # First: RBAC roles
2. src/02_policy_*/           # Second: Policy definitions
3. src/03_policy_set/         # Third: Policy initiatives
4. src/04_policy_assignments/ # Last: Assignments
```

### Project Structure

```
src/
├── 01_custom_roles/         # Custom RBAC roles
├── 02_policy_*/             # Policy definitions by domain
├── 03_policy_set/           # Policy initiatives
├── 04_policy_assignments/   # Assignments to MG/Subscriptions
└── scripts/                 # Utility scripts
```

### Common Commands

```bash
# Use the wrapper script
./terraform.sh plan
./terraform.sh apply
./terraform.sh destroy

# Force policy re-evaluation
az policy state trigger-scan --no-wait
```

### Naming Conventions

- Policies: `pagopa-<domain>-<rule>`
- Initiatives: `pagopa-<domain>-<env>`
- Roles: PascalCase descriptive names

## 🚫 Don't Do

- ❌ Skip apply order
- ❌ Hardcode subscription IDs
- ❌ Use overly broad role permissions
- ❌ Deploy to production without UAT testing
- ❌ Skip PR review process
