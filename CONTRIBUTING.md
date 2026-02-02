# Contributing to eng-azure-governance

## Quick Start

1. Clone the repository
2. Install required tools:
   - [tfenv](https://github.com/tfutils/tfenv) for Terraform version management
   - [pre-commit](https://pre-commit.com/) for Git hooks
3. Run `pre-commit install` to set up hooks

## Making Changes

### Important: Apply Order

Changes must be applied in folder number order:

1. `01_custom_roles` - RBAC role definitions
2. `02_policy_*` - Policy definitions
3. `03_policy_set` - Policy initiatives
4. `04_policy_assignments` - Assignments

### Adding Policies

1. Create in appropriate `02_policy_*` folder
2. Follow naming: `pagopa-<domain>-<rule>`
3. Include clear descriptions
4. Test with `./terraform.sh plan`

### Adding Initiatives

1. Create in `03_policy_set/`
2. Reference policies from `02_policy_*`
3. Use environment-specific naming

### Adding Custom Roles

1. Create in `01_custom_roles/`
2. Follow least privilege principle
3. Document permission justifications

## Conventions

### Commit Messages

Use conventional commits format:

```
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `chore`, `docs`, `ci`, `refactor`

### Terraform

- Run `terraform fmt` before committing
- Use `./terraform.sh` wrapper script
- Update lock file for multiple platforms

## Workflow

1. Create a feature branch from `main`
2. Make changes following apply order
3. Run `make lint` to validate
4. Open a Pull Request
5. Wait for CI checks and review
6. Merge after approval

## Getting Help

Contact the Cloud Engineering team for assistance.
