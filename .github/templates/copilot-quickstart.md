# Copilot Customization Quickstart

## Goal
Bootstrap a repository with a minimal, portable `.github` Copilot customization setup.

For detailed maintenance and validation flow, refer to `.github/README.md`.

## Steps
1. Copy baseline files:
   - `.github/copilot-instructions.md`
   - `.github/copilot-commit-message-instructions.md`
   - `.github/copilot-code-review-instructions.md`
2. Add stack-specific instruction files from `.github/instructions/`.
3. Add prompt files from `.github/prompts/` relevant to the team workflow.
4. Add matching skills from `.github/skills/` referenced by prompts.
5. Run `.github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.

## Suggested starter sets
- Java repositories: `java.instructions.md`, `cs-java.prompt.md`, `project-java/SKILL.md`
- Node.js repositories: `nodejs.instructions.md`, `cs-nodejs.prompt.md`, `project-nodejs/SKILL.md`
- CI-focused repositories: `github-actions.instructions.md`, `github-action.prompt.md`, `cicd-workflow/SKILL.md`

## Validation gate
Add `.github/workflows/github-validate-copilot-customizations.yml` to enforce consistency in pull requests.

## Bootstrap tip
Use `.github/scripts/bootstrap-copilot-config.sh --target <repo-path>` in dry-run first, then `--apply`.
