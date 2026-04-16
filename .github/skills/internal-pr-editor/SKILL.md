---
name: internal-pr-editor
description: Use when writing or updating a pull request title or body from a real diff, specification, or repository template, and the output must stay aligned with the actual change.
---

# Internal PR Editor

## When to use
- Create a new pull request description.
- Improve an incomplete pull request body.
- Summarize changes from modified files and checks.
- Map a specification, issue, or template-driven request into a PR title and body without overstating what the diff actually delivers.

## Mandatory rules
- Use English for all PR content.
- Keep summary concise and outcome-oriented.
- Include only relevant scope checkboxes.
- Provide a short bullet list of key changes.
- Include validation commands and results.
- Explicitly state risk level and rollback plan.
- If PR tools are available, apply updates to the PR directly.
- Do not modify any `README.md` file unless explicitly requested.

## Template resolution
Resolve and use one existing repository template:
1. `.github/PULL_REQUEST_TEMPLATE.md`
2. `.github/pull_request_template.md`
3. `PULL_REQUEST_TEMPLATE.md`
4. `pull_request_template.md`

Keep headings and section order unchanged. If a section is not applicable, write `N/A`.

## Specification-aware drafting

If the user provides a specification, issue, or acceptance outline:

- Extract the required outcomes, constraints, and acceptance points first.
- Map the actual diff to that requested scope instead of inventing completion.
- Call out anything requested by the specification that is not present in the diff as a gap, follow-up, or `N/A`.
- Keep the PR body grounded in the repository template, not in the source specification's original formatting.

## Tool-driven workflow
1. Detect whether an open PR exists for the current branch.
2. If PR exists → update title/body directly.
3. If PR does not exist → create a draft PR first.
4. Update PR title/body using template-compliant content.
5. Re-fetch PR and verify required section headings exist.
6. Return PR URL and a concise confirmation.
7. If PR tools are unavailable → return ready-to-paste markdown plus CLI fallback commands.

## Minimal example
- Input:
  - title: "Externalize Copilot inventory"
  - changed_files: "AGENTS.md, .github/INVENTORY.md, .github/copilot-instructions.md"
  - validation: "make lint"
- Expected output: Complete PR body with all required template sections and concise change bullets.

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Generic summary ("Various improvements") | Reviewers cannot assess impact or scope | Write specific outcome: "Adds region validation to SCP deploy pipeline" |
| Missing risk level or rollback plan | Reviewers approve without understanding blast radius | Always fill Risk and Rollback sections explicitly |
| Adding sections not in the repo template | Breaks template consistency across PRs | Use only the sections from the resolved template |
| Leaving placeholder text (`TODO`, `fill in`) | Looks unfinished, blocks approval | Fill every section with real content or `N/A` |
| Listing every changed file instead of summarizing | Noisy description that obscures intent | Group changes by purpose; detail only non-obvious changes |
| Not including validation commands and output | Reviewer has no confidence that code was tested | Always include the exact commands and their results |

## Cross-references
- **internal-change-impact-analysis** (`.github/skills/internal-change-impact-analysis/SKILL.md`): for change-impact analysis that feeds the risk section.
- **internal-code-review** (`.github/skills/internal-code-review/SKILL.md`): for the review that follows the PR.

## Validation
- Every template-defined section heading is present.
- `Changes` has concise bullets describing the real diff.
- Risk and rollback are explicit and actionable.
- Final PR body is persisted when tooling supports PR updates.
