---
name: pr-writing
description: Produce concise, complete pull request descriptions aligned with the repository PR template.
---

# PR Writing Skill

## When to use
- Create a new pull request description.
- Improve an incomplete pull request body.
- Summarize changes from modified files and checks.

## Mandatory rules
- Use English for all PR content.
- Keep summary concise and outcome-oriented.
- Include only relevant scope checkboxes.
- Provide a short bullet list of key changes.
- Include validation commands and results.
- Explicitly state risk level and rollback plan.
- If PR tools are available, apply updates to the PR (do not stop at generated markdown only).
- Do not modify any `README.md` file unless explicitly requested by the user.

## Template alignment
- Resolve and use one existing repository template path:
  - `.github/pull_request_template.md`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `pull_request_template.md`
  - `PULL_REQUEST_TEMPLATE.md`
- Keep headings and section order unchanged.
- If a section is not applicable, write `N/A`.
- Avoid leaving placeholders empty.

## Tool-driven workflow (VS Code / JetBrains)
1. Detect whether an open PR exists for the current branch.
2. If PR exists, update title/body directly.
3. If PR does not exist, create a draft PR first.
4. Update PR title/body using template-compliant content.
5. Re-fetch PR and verify required section headings exist in persisted body.
6. Return PR URL and a concise confirmation summary.
7. If PR tools are unavailable, return ready-to-paste markdown plus exact CLI fallback commands.

## Required section headings
- `## Summary`
- `## Scope`
- `## Changes`
- `## Validation`
- `## Security and Compliance`
- `## Risk and Rollback`
- `## Related Links`
- `## Reviewer Notes`

## Minimal example
- Input:
  - title: "Harden Copilot validator"
  - changed_files: ".github/scripts/validate-copilot-customizations.sh, .github/workflows/github-validate-copilot-customizations.yml"
  - validation: "bash -n scripts/*.sh; shellcheck -s bash scripts/*.sh"
- Expected output:
  - Complete PR body with all required template sections.
  - A brief and accurate bullet list under `Changes`.

## Validation
- Ensure every required section heading is present.
- Ensure `Changes` has concise bullets describing the real diff.
- Ensure risk and rollback are explicit and actionable.
- Ensure final PR body is persisted when tooling supports PR updates.
