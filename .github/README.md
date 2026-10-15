# .github Configuration

This folder contains repository Copilot review instructions, the local
retirement skill, and GitHub workflows.
The operating baseline is [AGENTS.md](../AGENTS.md), refined by
[AGENTS.local.md](../AGENTS.local.md). The [inventory](INVENTORY.md) lists the
assets actually installed in this checkout.

## Structure

- `copilot-instructions.md`: GitHub.com Copilot code-review guidance only
- `DEPRECATION.md`: lifecycle policy for prompts/skills/instructions/agents
- `instructions/`: path-specific auto-applied rules
- `prompts/`: reusable slash prompts
- `skills/`: reusable implementation capabilities
- `agents/`: optional custom chat agents
- `workflows/`: CI validation workflows

## Agent routing

No repository-local custom agents are installed. Use the editor's available
agent and the task-specific prompts or instructions. User-installed skills are
not repository-local copies. See the [agent catalog](agents/README.md).

## Maintenance workflow

1. Update files under `.github/`.
2. Update the inventory whenever a customization is added, removed, or renamed.
3. Run the native inventory test shown below and validate local documentation links.
4. Run checks owned by any changed workflow or component.
5. Record notable changes in the pull request; no local customization changelog is installed.

## Notes

- No repository-local bootstrap script or standalone customization validator is installed.
- User-installed tools do not establish repository policy or prove local asset availability.

## Validation

Run the [native inventory test](../tests/github/test_copilot_inventory.py)
with the existing retirement v2 environment after changing this directory:

```bash
src/comitato/comitato_azure_retirements_v2/.venv/bin/python -m pytest -q tests/github
```

No diagram is provided because this README is a directory navigation and
maintenance surface; the referenced catalog and native test define its
relationships more precisely than a duplicate diagram.
