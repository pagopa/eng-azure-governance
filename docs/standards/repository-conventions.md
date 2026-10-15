# Repository Conventions

Contributors use these conventions across the repository's four domains.

Serves: PUR, PRI-01, PRI-05

## STD-REPO-01 - Name governance policies consistently

- Convention: Custom policy names follow `pagopa-<domain>-<rule>` and include clear descriptions.
- Evidence: [Contribution conventions](../../CONTRIBUTING.md#adding-policies).
- Exceptions: none evidenced.

## STD-REPO-02 - Describe changes with conventional commits

- Convention: Commit messages use `<type>(<scope>): <description>` with the types listed in the contribution guide.
- Evidence: [Commit conventions](../../CONTRIBUTING.md#commit-messages).
- Exceptions: none evidenced.

## STD-REPO-03 - Use the owning Terraform wrapper

- Convention: Terraform lifecycle operations use the wrapper belonging to the target root. Arguments and backend layouts remain root-specific.
- Evidence: [Terraform conventions](../../CONTRIBUTING.md#terraform), [root usage](../../README.md#terraform), and [architecture](../architecture.md#9-configuration-and-environment).
- Exceptions: Backend-disabled validation and format checks use the non-mutating commands documented by the owning component.

The [contribution guide](../../CONTRIBUTING.md) remains the operational owner for onboarding and the contribution workflow. Domain invariants remain with their existing rule owners in the [documentation index](../README.md).
