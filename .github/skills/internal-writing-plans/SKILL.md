---
name: internal-writing-plans
description: Use when repository-owned work needs a retained numbered plan under tmp/superpowers/<clear-action-or-task-name>/ and the plan must follow the local Italian-default execution-plan contract.
---

# Internal Writing Plans

Use this skill as the repository-owned wrapper for plan authoring in this repository.

Treat `obra-writing-plans` as imported depth and keep any repo-local drift fixes narrow. This skill adds the local contract for when a plan is retained, where it lives, how numbered files are split, what language they use, and what must stay outside the execution loop.

## When to use

- Writing or rewriting a retained repository-owned execution plan under `tmp/superpowers/` when the work is non-banal.
- Retaining a plan because the work crosses turns, spans multiple macro-categories, needs handoff, tracking, or provenance, or carries tradeoffs or uncertainties that should stay reviewable.
- Converting a monolithic or overgrown plan into the local numbered-plan structure.
- Preparing a plan that will later be executed by `internal-executing-plans`.

## When not to use

- General design or spec work under `tmp/superpowers/specs/`; use `obra-brainstorming` when that workflow is relevant.
- Clear, local, quick, or banal tasks whose next steps fit in chat.
- Local execution with no retained plan artifact.
- Imported or sync-managed planning assets; do not edit `obra-*` skills to impose this policy.

## Local retained-plan contract

- Create or reuse a retained plan folder under `tmp/superpowers/<clear-action-or-task-name>/` only when the plan needs to survive the current turn.
- Keep planning ephemeral in chat when the task is clear, local, quick, or banal.
- Retain a plan only when at least one of these is true: the work crosses turns, spans multiple macro-categories, needs handoff, tracking, or provenance, or includes tradeoffs or uncertainties that should stay reviewable.
- Use a single numbered file such as `01-implementazione.md` when the work has one macro-category.
- Use multiple numbered Markdown files by macro-category, for example `01-contesto-e-vincoli.md`, `02-implementazione.md`, and `03-validazione.md`, when the work spans more than one macro-category.
- Do not keep one monolithic plan file when the work spans multiple macro-categories.
- Write those plan files in Italian by default unless the user explicitly asks for another language.
- Keep unresolved questions, doubts, and user decisions in `dubbi-e-domande.md`.
- `dubbi-e-domande.md` is not an execution-plan file and must stay outside the plan-and-apply loop.

## Numbered-file shape

- Optimize retained plan files for scanability and decision review rather than exhaustive prose.
- Prefer explicit headings and short bullets; avoid long paragraphs.
- Keep rationales brief and avoid duplicating context already captured in `AGENTS.md`, `.github/copilot-instructions.md`, or neighboring repository-owned assets.
- `Obiettivo`
- `Logica scelta`
- `Assunzioni chiave`
- `Passi eseguibili`
- `Validazione`
- Keep each section to 5-7 bullets when practical.
- Keep bullets to 1-2 lines when practical.
- Make each executable step easy to challenge, verify, or remove without rewriting the whole file.

## Relationship to OBRA

- Use this skill first for repository-owned planning policy.
- Reuse `obra-writing-plans` only for the remaining plan-authoring mechanics that do not conflict with the local contract.
- If the plan will be executed in the same repository-owned workflow, hand off to `internal-executing-plans` instead of routing directly to `obra-executing-plans`.

## Workflow

1. Decide first whether retained planning is justified or whether in-chat planning is enough.
2. Choose a clear task folder name under `tmp/superpowers/`.
3. Define the macro-categories first and choose the smallest numbered-file shape that fits the work.
4. Use a single `01-...md` file when one macro-category is enough, or create one numbered plan file per category when more than one macro-category exists.
5. Give each numbered file the shape above and keep every section compact.
6. Put open questions and decision requests only in `dubbi-e-domande.md`.
7. Keep executable next steps in the numbered plan files without mixing unresolved questions into them.

## Validation

- The plan exists only when retained planning is justified beyond the current turn.
- The plan lives under `tmp/superpowers/<clear-action-or-task-name>/`.
- A single `01-...` file is used when one macro-category is enough; `01-...`, `02-...`, `03-...` style plan files exist when more than one macro-category exists.
- Plan files are in Italian unless the user asked otherwise.
- The numbered files follow the local shape contract with explicit headings and short bullets.
- `dubbi-e-domande.md` exists when needed and remains separate from executable plan files.
- The plan does not rely on imported `obra-*` skills as the policy owner; any repo-local drift fix stays narrow and subordinate to this wrapper.

## Common mistakes

- Creating a retained plan artifact for a clear, local, quick task that should stay in chat.
- Writing the whole plan in one Markdown file.
- Writing long narrative paragraphs or duplicating canonical context instead of keeping the plan scannable.
- Mixing executable checklist items with open questions.
- Putting the plan under `docs/` instead of `tmp/superpowers/`.
- Switching the whole repository to Italian instead of keeping the exception local to plan files.
