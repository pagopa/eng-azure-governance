# Commit Message Instructions - eng-azure-governance

## Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## Types

| Type | When to Use |
|------|-------------|
| `feat` | New policy, role, or initiative |
| `fix` | Correct policy definitions or bugs |
| `chore` | Maintenance, dependency updates |
| `docs` | Documentation changes |
| `ci` | CI/CD workflow changes |
| `refactor` | Code restructuring without behavior change |

## Scopes

| Scope | Description |
|-------|-------------|
| `roles` | Custom RBAC roles |
| `policy` | Policy definitions |
| `initiative` | Policy initiatives/sets |
| `assignment` | Policy assignments |
| `<domain>` | Domain-specific (e.g., `storage`, `networking`, `cosmosdb`) |

## Examples

```
feat(policy): add encryption requirement for storage accounts

- Denies creation of unencrypted storage accounts
- Applies to all subscriptions
```

```
feat(initiative): create CosmosDB compliance initiative for prod

Groups all CosmosDB policies for production environment
```

```
feat(roles): add AppServiceReader custom role

Minimal read permissions for App Service monitoring
```

```
fix(assignment): correct scope for networking policy

Changed from subscription to management group level
```

## Rules

1. Use imperative mood ("add" not "added")
2. First line max 72 characters
3. Reference ticket numbers when applicable
4. Explain the "why" for policy changes
