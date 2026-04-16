# Review Checklist

Load this file before finalizing, replacing, or deleting an instruction file.

## Structural Checks

- The file still belongs in `instructions/` rather than `skills/`, `AGENTS.md`, or `.github/copilot-instructions.md`.
- The filename uses the repository-owned lowercase hyphenated `.instructions.md` form.
- Frontmatter uses only `description` and `applyTo`.
- The title and section layout are readable without becoming encyclopedic.

## Content Checks

- Rules are imperative, specific, and non-contradictory.
- Examples are included only when they clarify a non-obvious pattern.
- Tables, comparisons, and links are present only when they materially improve decisions.
- Validation commands are real for the target stack or omitted when they would be speculation.
- Example snippets, glob patterns, and commands are concrete enough to survive direct reuse.
- The instruction does not ask the model to stop and ask a preference question during normal auto-load use.

## Catalog Checks

- `INVENTORY.md` matches the live instruction list.
- `.github/README.md` counts and family summaries match the catalog after adds or removals.
- `.github/agents/internal-sync-control-center.agent.md` still reflects the managed imported instruction list after imported assets are replaced or retired.

## Replacement Checks

- If an imported `awesome-*` instruction was replaced, the repository-owned replacement has a distinct `internal-*` identity.
- The replacement is not a 1:1 dump of the old content; it has a tighter trigger and a clearer boundary.
