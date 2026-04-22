---
name: internal-executing-plans
description: Use when executing a repository-owned plan from tmp/superpowers/<clear-action-or-task-name>/ and the done-* loop, numbered file order, and blocker handling must stay explicit.
---

# Internal Executing Plans

Use this skill as the repository-owned wrapper for applying retained numbered plans in this repository.

Treat `obra-executing-plans` and `obra-subagent-driven-development` as imported execution depth and keep any repo-local drift fixes narrow. This skill adds the local execution loop for one or more numbered plan files and `done-*` tracking.

## When to use

- Executing a repository-owned plan from `tmp/superpowers/<clear-action-or-task-name>/`.
- Applying a plan that was authored with `internal-writing-plans`.
- Converting inline progress tracking into the repository `done-*` loop.

## When not to use

- Reviewing or challenging a plan before execution; stay with `internal-planning-leader` or `internal-review-guard` as appropriate.
- Treating `dubbi-e-domande.md` as an executable plan file.
- Editing imported `obra-*` assets to change execution behavior.

## Execution contract

- Read the numbered plan files in order.
- Ignore `dubbi-e-domande.md` during plan application. It stays outside the plan-and-apply loop.
- For each active plan file, create or update the matching `done-<source-file-name>.md` file.
- When an item is completed, move it into the matching `done-*` file and remove it from the active plan file.
- Delete an active plan file once all of its executable items have been moved out and the file is empty.
- Continue automatically to the next remaining numbered plan file until no numbered plan files remain.
- Stop only for real blockers that require user input, missing prerequisites, or a materially broken plan.

## Relationship to execution engines

- Use this skill first for the repository-local execution policy.
- Use `obra-subagent-driven-development` when same-session subagents are truly available and the plan benefits from worker isolation or staged parallelism.
- Otherwise use `obra-executing-plans` for the underlying step-by-step execution engine.
- Do not let imported execution skills override the local `done-*` loop, file ordering, or blocker rules.

## Workflow

1. Load the task folder and identify all remaining numbered plan files.
2. Process the lowest-numbered remaining plan file first.
3. Execute items, verify them, and move completed items to the matching `done-*` file.
4. Remove completed items from the active source file.
5. Delete an active plan file when no executable items remain.
6. Repeat until all numbered plan files are cleared.
7. Ask the user for input only when a real blocker prevents safe continuation.

## Validation

- `dubbi-e-domande.md` was excluded from execution.
- Matching `done-*` files exist for plan files that started execution.
- Completed items no longer remain in the active numbered plan file.
- Empty source plan files are deleted.
- Execution continued across remaining numbered plan files until completion or a real blocker.
- Imported execution skills were used only as engines, not rewritten as policy containers.

## Common mistakes

- Checking items off in place but leaving them in the active plan file.
- Treating `dubbi-e-domande.md` as a task list.
- Stopping after one numbered file even though others remain.
- Asking the user for routine confirmations instead of only for real blockers.
