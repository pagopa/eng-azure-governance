# AGENTS.md - eng-azure-governance

This file is for GitHub Copilot and AI assistants working in this repository.

## Naming Policy
- Use GitHub Copilot terminology in repository-facing content.
- Do not mention internal runtime names in repository artifacts.
- Treat prompt frontmatter `name:` as the canonical command identifier.
- Repository-internal prompt, skill, and agent filenames must start with `internal-`.
- Repository-internal prompt, skill, and agent `name:` values must also start with `internal-`.

## Decision Priority
1. Apply repository non-negotiables from `.github/copilot-instructions.md`.
2. Apply explicit user requirements for the current task.
3. Apply the selected agent behavior (agent-first routing).
4. Apply matching files under `.github/instructions/*.instructions.md` using `applyTo`.
5. Apply selected prompt constraints from `.github/prompts/*.prompt.md`.
6. Apply implementation details from referenced `.github/skills/*/SKILL.md`.
7. If no agent is explicitly selected, default to `TechAIImplementer`.

## Agent Routing

### When to use each agent
- Use `TechAIPlanner` for ambiguous scope, tradeoff analysis, or multi-step design.
- Use `TechAIImplementer` for direct code/config changes and validation-first delivery.
- Use `TechAIReviewer` for quality gates and defect/regression findings.
- Use `TechAITerraformGuardrails` for Terraform safety and policy guardrail reviews.
- Use `TechAIIAMLeastPrivilege` for role and permission scoping checks.
- Use `TechAIWorkflowSupplyChain` for workflow supply-chain hardening and CI checks.
- Use `TechAISecurityReviewer` as the security-focused review gate.
- Use `TechAIPRWriter` when generating pull request content from the repository template.

### Agent composition
- For changes spanning multiple specialist domains, run each relevant specialist and aggregate findings.
- The standard chain for non-trivial work is: `TechAIPlanner` -> `TechAIImplementer` -> `TechAIReviewer` or a matching specialist.

## Governance References
- `.github/security-baseline.md`
- `.github/DEPRECATION.md`
- `.github/repo-profiles.yml`
- `.github/scripts/validate-copilot-customizations.sh`

## Prohibitions
- Apply all non-negotiables from `.github/copilot-instructions.md` plus:
- Never run destructive commands unless explicitly requested.
- Never skip validation after making changes.

## Repository Defaults
- Primary focus: Infrastructure governance repository for policies, assignments, and custom roles.
- Profile hint: `infrastructure-heavy`
- AGENTS.md is the external bridge for assistant behavior and naming; keep runtime references abstract.
- Resolve stack from target files and explicit prompt inputs; the agent role remains behavioral, not language-specific.
- Prioritize these paths:
  - `src/01_custom_roles`
  - `src/02_policy_*`
  - `src/03_policy_set`
  - `src/04_policy_assignments`
  - `src/scripts`

### Default instruction routing
| Pattern | Instruction |
| --- | --- |
| `**/*.sh` | `bash.instructions.md` |
| `**/workflows/**` | `github-actions.instructions.md` |
| `**/authorizations/**/*.json,**/organization/**/*.json,**/src/**/*.json,**/data/**/*.json` | `json.instructions.md` |
| `**/Makefile,**/*.mk` | `makefile.instructions.md` |
| `**/*.md` | `markdown.instructions.md` |
| `**/*.sh,**/scripts/**/*.py,**/bin/**/*.py,**/*script*.py` | `scripts.instructions.md` |
| `**/*.tf` | `terraform.instructions.md` |
| `**/*.yml,**/*.yaml` | `yaml.instructions.md` |

### Preferred prompts
- `TechAICloudPolicy`
- `TechAITerraform`

### Preferred skills
- `TechAICloudPolicy`
- `TechAITerraformFeature`
- `TechAITerraformModule`

### Required validations before PR
- `terraform fmt -recursive`
- `terraform validate`
- `bash -n <changed_bash_paths>`
- `shellcheck -s bash <changed_bash_paths>`
- `bash .github/scripts/validate-copilot-customizations.sh --scope root --mode strict`

## Repository Inventory (Auto-generated)
This inventory reflects the desired managed baseline plus repository-owned internal Copilot assets already present in the target repository.

### Instructions
- `.github/instructions/bash.instructions.md`
- `.github/instructions/github-action-composite.instructions.md`
- `.github/instructions/github-actions.instructions.md`
- `.github/instructions/json.instructions.md`
- `.github/instructions/makefile.instructions.md`
- `.github/instructions/markdown.instructions.md`
- `.github/instructions/python.instructions.md`
- `.github/instructions/scripts.instructions.md`
- `.github/instructions/terraform.instructions.md`
- `.github/instructions/yaml.instructions.md`

### Prompts
- `.github/prompts/create-custom-role.prompt.md`
- `.github/prompts/create-initiative.prompt.md`
- `.github/prompts/create-policy.prompt.md`
- `.github/prompts/cs-add-unit-tests.prompt.md`
- `.github/prompts/cs-python-script.prompt.md`
- `.github/prompts/cs-python.prompt.md`
- `.github/prompts/github-composite-action.prompt.md`
- `.github/prompts/script-python.prompt.md`
- `.github/prompts/tech-ai-bash-script.prompt.md`
- `.github/prompts/tech-ai-cloud-policy.prompt.md`
- `.github/prompts/tech-ai-data-registry.prompt.md`
- `.github/prompts/tech-ai-github-action.prompt.md`
- `.github/prompts/tech-ai-github-pr-description.prompt.md`
- `.github/prompts/tech-ai-terraform.prompt.md`
- `.github/prompts/terraform-module.prompt.md`

### Skills
- `.github/skills/composite-action/SKILL.md`
- `.github/skills/project-python/SKILL.md`
- `.github/skills/script-python/SKILL.md`
- `.github/skills/tech-ai-cicd-workflow/SKILL.md`
- `.github/skills/tech-ai-cloud-policy/SKILL.md`
- `.github/skills/tech-ai-data-registry/SKILL.md`
- `.github/skills/tech-ai-pr-writing/SKILL.md`
- `.github/skills/tech-ai-script-bash/SKILL.md`
- `.github/skills/tech-ai-terraform-feature/SKILL.md`
- `.github/skills/tech-ai-terraform-module/SKILL.md`

### Agents
- `.github/agents/tech-ai-github-pr-writer.agent.md`
- `.github/agents/tech-ai-github-workflow-supply-chain.agent.md`
- `.github/agents/tech-ai-iam-least-privilege.agent.md`
- `.github/agents/tech-ai-implementer.agent.md`
- `.github/agents/tech-ai-planner.agent.md`
- `.github/agents/tech-ai-reviewer.agent.md`
- `.github/agents/tech-ai-security-reviewer.agent.md`
- `.github/agents/tech-ai-terraform-guardrails.agent.md`
