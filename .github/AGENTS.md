# AGENTS.md - eng-azure-governance

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy
- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal runtime names in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.

## Decision Priority
1. Apply repository non-negotiables from `copilot-instructions.md`.
2. Apply explicit user requirements for the current task.
3. Apply the selected agent behavior (agent-first routing).
4. Apply matching files under `instructions/*.instructions.md` using `applyTo`.
5. Apply selected prompt constraints from `prompts/*.prompt.md`.
6. Apply implementation details from referenced `skills/*/SKILL.md`.
7. If no agent is explicitly selected, default to `Implementer`.

## Stack Resolution Rules
- The agent role is behavioral, not language-specific.
- Resolve stack from target files and explicit prompt inputs.
- Primary `applyTo` rules (one instruction per file type):
  - `**/*.py` -> `instructions/python.instructions.md`
  - `**/*.java` -> `instructions/java.instructions.md`
  - `**/*.sh` -> `instructions/bash.instructions.md`
  - `**/*.tf` -> `instructions/terraform.instructions.md`
  - `**/*.js,**/*.cjs,**/*.mjs,**/*.ts,**/*.tsx` -> `instructions/nodejs.instructions.md`
  - `**/*.yml,**/*.yaml` -> `instructions/yaml.instructions.md`
  - `**/*.md` -> `instructions/markdown.instructions.md`
  - `**/Makefile,**/*.mk` -> `instructions/makefile.instructions.md`
  - `**/workflows/**` -> `instructions/github-actions.instructions.md`
  - `**/actions/**/action.y*ml` -> `instructions/github-action-composite.instructions.md`
  - `**/authorizations/**/*.json,**/organization/**/*.json,**/src/**/*.json,**/data/**/*.json` -> `instructions/json.instructions.md`
- Overlay rules (additive — apply alongside the primary instruction above):
  - `**/*.sh,**/scripts/**/*.py,**/scripts/**/*.sh` -> `instructions/scripts.instructions.md`
  - `**/*lambda*.tf,**/*lambda*.py,**/*lambda*/**` -> `instructions/lambda.instructions.md`
- If a change spans multiple stacks, apply all relevant instruction files.
- Overlay instructions never conflict with primary instructions — they add cross-cutting standards.

## Agent Routing

### When to use each agent
- Use `Planner` for ambiguous scope, tradeoff analysis, or multi-step design.
- Use `Implementer` for direct code/config changes and validations.
- Use `Reviewer` for quality gates and defect/regression findings.
- Use specialist agents (`WorkflowSupplyChain`, `SecurityReviewer`, `TerraformGuardrails`, `IAMLeastPrivilege`, `PRWriter`) only when their domain matches the task.

### When NOT to use (anti-patterns)
- Do not use `Planner` for trivial single-file changes with clear requirements — go directly to `Implementer`.
- Do not use `Implementer` when requirements are ambiguous or scope is unclear — use `Planner` first.
- Do not use generic `Reviewer` when the change is purely Terraform, IAM, workflows, or security — use the matching specialist instead.

### Agent composition
- For changes spanning multiple specialist domains (e.g., Terraform + IAM), run each relevant specialist and aggregate findings.
- The standard chain for non-trivial work is: `Planner` → `Implementer` → `Reviewer` (or specialist reviewer).

### Handoff protocol
- Planner output (implementation plan) is input context for Implementer.
- Implementer output (list of changed files + validation results) is input context for Reviewer.
- Reviewer findings flagged as `Critical` or `Major` route back to Implementer for remediation.

## Available Skills
- `cicd-workflow` (`skills/cicd-workflow/SKILL.md`): GitHub Actions workflow design and CI/CD patterns.
- `cloud-policy` (`skills/cloud-policy/SKILL.md`): AWS SCP, Azure Policy, GCP Org Policy governance.
- `composite-action` (`skills/composite-action/SKILL.md`): Reusable GitHub composite actions.
- `data-registry` (`skills/data-registry/SKILL.md`): JSON data registry entries and schema patterns.
- `pr-writing` (`skills/pr-writing/SKILL.md`): PR title/body generation from template and diff.
- `project-java` (`skills/project-java/SKILL.md`): Java service code with DDD, Spring Boot, JUnit 5.
- `project-nodejs` (`skills/project-nodejs/SKILL.md`): Node.js service code with DDD, ESM, node:test.
- `project-python` (`skills/project-python/SKILL.md`): Python project code with DDD, pytest, type hints.
- `script-bash` (`skills/script-bash/SKILL.md`): Bash utility scripts with strict mode and shellcheck.
- `script-python` (`skills/script-python/SKILL.md`): Python utility scripts with argparse and tests.
- `terraform-feature` (`skills/terraform-feature/SKILL.md`): Terraform feature implementation patterns.
- `terraform-module` (`skills/terraform-module/SKILL.md`): Terraform reusable module design.

## Available Prompts
- `cs-add-unit-tests` (`prompts/cs-add-unit-tests.prompt.md`): Add or improve unit tests.
- `cs-bash-script` (`prompts/cs-bash-script.prompt.md`): Create or modify Bash scripts.
- `cs-cloud-policy` (`prompts/cs-cloud-policy.prompt.md`): Create cloud governance policies.
- `cs-data-registry` (`prompts/cs-data-registry.prompt.md`): Create JSON data registry entries.
- `cs-java` (`prompts/cs-java.prompt.md`): Generate Java service code.
- `cs-nodejs` (`prompts/cs-nodejs.prompt.md`): Generate Node.js service code.
- `cs-python-script` (`prompts/cs-python-script.prompt.md`): Create Python utility scripts.
- `cs-python` (`prompts/cs-python.prompt.md`): Generate Python project code.
- `cs-terraform` (`prompts/cs-terraform.prompt.md`): Create Terraform modules and features.
- `cs-github-action` (`prompts/github-action.prompt.md`): Create GitHub Actions workflows.
- `cs-composite-action` (`prompts/github-composite-action.prompt.md`): Create composite actions.
- `cs-pr-description` (`prompts/github-pr-description.prompt.md`): Generate PR descriptions.

## Governance References
- `security-baseline.md`: Portable security controls baseline for all Copilot customization.
- `DEPRECATION.md`: Lifecycle and deprecation policy for all customization assets.
- `repo-profiles.yml`: Advisory profile catalog for different repository types.
- `scripts/validate-copilot-customizations.sh`: Validation gate for customization changes.
- `templates/AGENTS.template.md`: Template for onboarding new repositories.
- `templates/copilot-quickstart.md`: Quick start guide for new teams.

## Template Placeholders
- `CODEOWNERS` may keep `@your-org/platform-governance-team` only in template repositories.
- Consumer repositories must replace placeholder owners before enabling review enforcement.
- The validator should warn when the placeholder owner is still present.

## Prohibitions
- Never hardcode secrets, tokens, or credentials.
- Never modify `README.md` files unless explicitly requested by the user.
- Never introduce new patterns when existing repository conventions exist.
- Keep all repository artifacts in English (user chat may be in other languages).
- Never run destructive commands unless explicitly requested.
- Never skip validation after making changes.

## PR and Workflow Conventions
- PR content must follow `pull_request_template.md` in exact section order.
- For GitHub Actions pinning, each full SHA must include an adjacent comment with release/tag reference.

## Backlog Triggers
- Add `instructions/docker.instructions.md` when the first Dockerfile is introduced in this repository.

## Repository Inventory (Auto-generated)
### Instructions
- `instructions/bash.instructions.md`
- `instructions/github-action-composite.instructions.md`
- `instructions/github-actions.instructions.md`
- `instructions/java.instructions.md`
- `instructions/json.instructions.md`
- `instructions/lambda.instructions.md`
- `instructions/makefile.instructions.md`
- `instructions/markdown.instructions.md`
- `instructions/nodejs.instructions.md`
- `instructions/python.instructions.md`
- `instructions/scripts.instructions.md`
- `instructions/terraform.instructions.md`
- `instructions/yaml.instructions.md`

### Prompts
- `prompts/cicd-workflow.prompt.md`
- `prompts/create-custom-role.prompt.md`
- `prompts/create-initiative.prompt.md`
- `prompts/create-policy.prompt.md`
- `prompts/cs-add-unit-tests.prompt.md`
- `prompts/cs-bash-script.prompt.md`
- `prompts/cs-cloud-policy.prompt.md`
- `prompts/cs-data-registry.prompt.md`
- `prompts/cs-java.prompt.md`
- `prompts/cs-nodejs.prompt.md`
- `prompts/cs-python-script.prompt.md`
- `prompts/cs-python.prompt.md`
- `prompts/cs-terraform.prompt.md`
- `prompts/github-action.prompt.md`
- `prompts/github-composite-action.prompt.md`
- `prompts/github-pr-description.prompt.md`
- `prompts/script-bash.prompt.md`
- `prompts/script-python.prompt.md`
- `prompts/terraform-module.prompt.md`

### Skills
- `skills/cicd-workflow/SKILL.md`
- `skills/cloud-policy/SKILL.md`
- `skills/composite-action/SKILL.md`
- `skills/data-registry/SKILL.md`
- `skills/pr-writing/SKILL.md`
- `skills/project-java/SKILL.md`
- `skills/project-nodejs/SKILL.md`
- `skills/project-python/SKILL.md`
- `skills/script-bash/SKILL.md`
- `skills/script-python/SKILL.md`
- `skills/terraform-feature/SKILL.md`
- `skills/terraform-module/SKILL.md`

### Agents
- `agents/github-pr-writer.agent.md`
- `agents/github-workflow-supply-chain.agent.md`
- `agents/iam-least-privilege.agent.md`
- `agents/implementer.agent.md`
- `agents/planner.agent.md`
- `agents/reviewer.agent.md`
- `agents/security-reviewer.agent.md`
- `agents/terraform-guardrails.agent.md`
