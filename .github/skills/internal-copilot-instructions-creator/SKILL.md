---
name: internal-copilot-instructions-creator
description: Use when creating, revising, splitting, replacing, or retiring repository-owned instruction files under `.github/instructions/`, especially when `applyTo` scope or precedence needs tightening.
---

# Internal Copilot Instructions Creator

Use this skill when the output should be an auto-applied instruction file. If the guidance is repo-wide, update `AGENTS.md` or `.github/copilot-instructions.md` instead. If the guidance is procedural or on-demand, create a skill or prompt instead of an instruction.

## When to use

- Create, revise, split, replace, or retire a repository-owned instruction under `.github/instructions/`.
- Tighten `applyTo` scope or instruction precedence for a path-specific guidance file.
- Decide whether a rule should live in an instruction instead of a repo-wide policy, skill, or prompt.

## Workflow

1. Choose the right artifact first.
   Use an instruction only for path-scoped rules that should auto-apply by file family. Do not turn repository governance, long workflows, or optional deep expertise into an instruction.
2. Define the narrowest valid `applyTo`.
   Scope by extension, directory, or concrete path pattern so the instruction fires only where it adds value.
3. Set the file identity explicitly.
   Keep instruction files under `.github/instructions/` and use lowercase hyphenated names ending in `.instructions.md`.
4. Keep frontmatter minimal and the body lean.
   Use only `description` and `applyTo` in frontmatter, then write short, imperative guidance with only the sections that materially help.
5. Structure for quick scanning, not for bulk.
   Start with a clear title, add only the sections that materially help, and use examples, code comparisons, or tables only when they clarify a non-obvious pattern.
6. Prefer local projection over generic encyclopedia.
   Capture repository-relevant expectations, naming, validation, and layering. Link reasoning only when it improves decisions.
7. Cover only the practices the boundary actually needs.
   Include naming, organization, dependencies, error handling, security, performance, testing, documentation, or version notes only when they materially affect that file family.
8. Validate overlap before finalizing.
   Check whether the rule belongs in a narrower instruction, an existing skill, or the repo-wide projection instead of creating another broad instruction.

## What Good Instructions Do

- Auto-apply to a clearly bounded file family.
- Add concrete, actionable rules that nearby files do not already make obvious.
- Stay short enough that routine edits are not forced to load irrelevant domain material.
- Reflect this repository's precedence model instead of re-owning global policy.
- Keep examples, links, and validation commands current and believable for the actual stack.

## References

- Load `references/frontmatter-and-scope.md` when creating a new instruction or changing `applyTo`.
- Load `references/review-checklist.md` before finalizing an instruction, replacing an imported instruction, or deleting one from the live catalog.

## Guardrails

- Do not include interactive questions or "ask the developer first" logic in an auto-loaded instruction.
- Do not duplicate large chunks of `AGENTS.md`, `.github/copilot-instructions.md`, or an existing internal skill.
- Do not use an instruction as a dumping ground for every best practice in a language or framework.
- Do not keep imported `awesome-*` instruction files once a repository-owned replacement exists.
- Do not leave catalog references stale after adding or removing an instruction.
- Do not keep decorative examples, tables, or resource links that do not change implementation choices.

## Validation

- Inspect nearby instruction files and follow existing frontmatter and prose patterns.
- Re-check that example globs, commands, and snippets are correct enough to survive direct reuse.
- Smoke-test the replacement mentally against a representative Copilot authoring request before retiring an imported guide.
- Re-check `.github/INVENTORY.md`, `.github/README.md`, and `.github/agents/local-sync-external-resources.agent.md` when the live instruction catalog changes.
