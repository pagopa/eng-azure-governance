# Copilot Instructions Override

This file is the consumer-local exception layer authorized by `AGENTS.md` and referenced by `.github/copilot-instructions.md`.

In the standards repository it lives as `.github/copilot-instructions.override.md.template`.
Sync materializes that template into consumer repositories as `.github/copilot-instructions.override.md`.
After materialization, the target repository owns the local exceptions declared there.

## Status

- No active overrides in this repository.
- When this section stays true, follow the synced baseline from `AGENTS.md` and `.github/copilot-instructions.md`.

## Activation Contract

Activate an override only when the repository needs a real local exception that should survive baseline sync updates.

Each active override must include:

- `Baseline rule`: the synced rule being overridden.
- `Local scope`: the files, paths, workflows, or situations where the exception applies.
- `Reason`: why the local repository needs the exception.
- `Required disclosure`: the sentence that must be surfaced when the override is followed.
- `Local instruction`: the replacement rule that applies inside the declared scope.

## Override Template

Copy this block for each active exception and replace the placeholders.

### Override: `<short-name>`

- `Baseline rule`: `<quote or summarize the synced rule being overridden>`
- `Local scope`: `<paths, file families, workflows, or request types>`
- `Reason`: `<why this repository needs the exception>`
- `Required disclosure`: `Consumer-local exception in effect from .github/copilot-instructions.override.md: <short disclosure>`
- `Local instruction`: `<the replacement behavior that applies in the declared scope>`
