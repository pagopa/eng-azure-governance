# .github Configuration

This folder contains global Copilot/Codex customization that can be reused across repositories.

## Structure
- `copilot-instructions.md`: global baseline rules
- `copilot-commit-message-instructions.md`: commit message policy
- `copilot-code-review-instructions.md`: review policy
- `repo-profiles.yml`: reusable high-level profile catalog for different repo types
- `security-baseline.md`: portable security baseline checklist
- `DEPRECATION.md`: lifecycle policy for prompts/skills/instructions/agents
- `instructions/`: path-specific auto-applied rules
- `prompts/`: reusable slash prompts
- `skills/`: reusable implementation capabilities
- `agents/`: optional custom chat agents
- `scripts/`: validation scripts
- `workflows/`: CI validation workflows
- `templates/`: reusable templates (for example `AGENTS.md`)

## Agent routing
- Read-only agents: `Planner`, `Reviewer`, `SecurityReviewer`, `WorkflowSupplyChain`, `TerraformGuardrails`, `IAMLeastPrivilege`
- Write-capable agent: `Implementer`

See `.github/agents/README.md` for details.

## Maintenance workflow
1. Update files under `.github/`.
2. Run `.github/scripts/validate-copilot-customizations.sh --scope root --mode strict`.
3. Optional: generate a machine-readable summary with `.github/scripts/validate-copilot-customizations.sh --scope root --mode strict --report json --report-file /tmp/copilot-report.json`.
4. Optional: bootstrap this configuration into another repository with `.github/scripts/bootstrap-copilot-config.sh --target <repo-path>` (default excludes apply; see `.github/.bootstrap-ignore`).
5. Optionally run cross-repo assessment with `.github/scripts/validate-copilot-customizations.sh --scope all --mode legacy-compatible`.
6. Ensure workflow checks pass.
7. Update `.github/CHANGELOG.md` for notable changes.

## Notes
- `repo-profiles.yml` is currently advisory (human-readable profile catalog).
- Use `templates/copilot-quickstart.md` for a short onboarding flow.
