---
name: internal-github-action-composite
description: Use when creating or modifying a reusable GitHub composite action under `.github/actions/`, especially when input validation, shell safety, or contract compatibility matters.
---

# GitHub Composite Action Skill

## When to use
- Create a new reusable composite action under `.github/actions/`.
- Modify an existing composite action and preserve compatibility.
- Deepen a GitHub Actions task that has already been classified as composite-action authoring.
- Add or revise composite-action documentation, outputs, testing guidance, or release discipline.

## Relationship to the umbrella skill
- `internal-github-actions` is the default entry point for GitHub Actions authoring.
- Load this skill when the work is specifically a composite action or when the umbrella skill decides the reusable unit should move here.

## Composite action vs reusable workflow

| Factor | Composite action | Reusable workflow |
|---|---|---|
| Granularity | Step-level reuse inside a job | Job-level orchestration |
| Secrets access | Inherited from the caller job | Passed explicitly to the called workflow |
| Outputs | Step outputs only | Workflow outputs |
| Best for | Shared validation, setup, or step logic | Pipelines with their own jobs, runners, or environments |

## Mandatory rules
- Follow `.github/instructions/internal-github-action-composite.instructions.md`.
- Pass expression inputs via `env:` instead of interpolating `${{ }}` directly in `run:`.
- Keep `shell: bash` explicit on composite steps.
- Start shell blocks with `set -euo pipefail`.
- Forward caller-visible values through action `outputs:` mapped from `$GITHUB_OUTPUT`.
- Use `$GITHUB_ENV` only for step-to-step state inside the action.
- Extract long shell logic into a dedicated script early.
- Preserve backward compatibility when modifying existing inputs or outputs.

## Reference map

- Load [minimal template](references/minimal-template.md) for the smallest safe starter `action.yml`.
- Load [multi-step template](references/multi-step-template.md) when the action coordinates validation, shared state, and caller-visible outputs across several steps.
- Load [output forwarding pattern](references/output-forwarding-pattern.md) when a step result must become a documented action output.
- Load [testing pattern](references/testing-pattern.md) for smoke workflow, failure-path, and contract checks.
- Load [action README template](references/action-readme-template.md) to document inputs, outputs, side effects, and usage.
- Load [versioning strategy](references/versioning-strategy.md) when the action is published or compatibility-sensitive.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Interpolating `${{ inputs.x }}` directly in `run:` | Crafted input values can turn into shell injection | Pass the value through `env:` and use quoted shell variables |
| Missing `set -euo pipefail` in `run:` blocks | Silent failures and partial execution become hard to spot | Make strict mode the first line of every shell block |
| Large inline `run:` blocks | They are hard to read, lint, and review | Extract the logic into a dedicated script early |
| No input validation before the main logic | Failures surface later with weaker error messages | Validate required inputs in the first step and fail fast |
| Forgetting `shell: bash` on composite steps | Runner defaults can differ and change behavior | Keep `shell: bash` explicit |
| Hiding caller-visible values in `$GITHUB_ENV` or temp files | Callers cannot read the value and the contract stays implicit | Forward the value through `$GITHUB_OUTPUT` and `outputs:` |
| Leaving outputs or usage undocumented | Consumers guess the contract and misuse the action | Keep a minimal README with inputs, outputs, side effects, and an example |
| Breaking an existing input or output contract | Callers can fail without a clear migration path | Add new fields compatibly and preserve the old contract where possible |

## Cross-references

- **internal-github-actions** (`.github/skills/internal-github-actions/SKILL.md`): for the umbrella GitHub Actions lane and reuse-pattern selection.
- **internal-script-bash** (`.github/skills/internal-script-bash/SKILL.md`): for extracted shell scripts inside the action.

## Validation checklist

- [ ] Inputs and outputs are explicit.
- [ ] Required inputs are validated in the first step.
- [ ] Multi-step state uses `$GITHUB_OUTPUT` and `$GITHUB_ENV` intentionally.
- [ ] Longer logic lives in a dedicated script.
- [ ] The README example matches the real inputs and outputs.
- [ ] A happy-path smoke validation exists.
- [ ] Existing input and output names remain compatible, or the breaking change is versioned deliberately.

## Validation

- Inputs and outputs are explicit and validated early.
- Shell code uses `set -euo pipefail`, quoted variables, and explicit `shell: bash`.
- A smoke workflow or equivalent fixture validates the happy path.
- Caller-visible outputs are forwarded through documented `outputs:` mappings.
- Existing input and output contracts remain backward compatible.
