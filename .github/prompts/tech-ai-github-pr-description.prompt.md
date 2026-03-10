---
description: Build a complete pull request body using the existing repository PR template
name: TechAIPRDescription
agent: TechAIPRWriter
argument-hint: title=<text> intent=<text> changed_files=<comma-separated paths> [validation=<commands/results>] [risk=<Low|Medium|High>] [links=<issue/docs/runbook>] [target_branch=<name>] [pr_number=<number>]
---

# Pull Request Description Task

## Context
Create or update a pull request body using the repository template (`.github/pull_request_template.md` or `pull_request_template.md`), including a short list of key changes.

## Required inputs
- **Title**: ${input:title}
- **Intent**: ${input:intent}
- **Changed files**: ${input:changed_files}
- **Validation**: ${input:validation:Not provided}
- **Risk**: ${input:risk:Low,Medium,High}
- **Links**: ${input:links:N/A}

## Template-derived structure
- Use the exact section headings from the resolved repository template.
- Keep template section order unchanged.
- Preserve any checklist section and mark items intentionally.
- Do not add extra sections unless the template already includes them.

## Instructions
1. Use `.github/skills/tech-ai-pr-writing/SKILL.md`.
2. Resolve the template path in this order:
   - `.github/pull_request_template.md`
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `pull_request_template.md`
   - `PULL_REQUEST_TEMPLATE.md`
3. Follow template section order and headings exactly as defined by the resolved template.
4. Answer every prompt/question line from the template explicitly with repository facts.
5. Preserve checklist items and mark each one intentionally (`[x]` or `[ ]`) based on real scope.
6. Do not remove required template sections; fill not-applicable content with `N/A`.
7. In `Changes`, provide brief bullets aligned to `changed_files`.
8. In scope or target-context sections, fill repository-specific fields explicitly when relevant, such as environments, services, identities, subscriptions, projects, or temporary access.
9. Keep content concise, concrete, and in English.
10. If PR tools are available:
   - update existing PR when found
   - otherwise create draft PR and then update title/body
   - verify persisted body includes all required headings and checklist lines
11. If PR tools are unavailable, return ready-to-paste markdown plus exact CLI fallback commands.

## Minimal example
- Input: `title="Add JSON report support in validator" intent="Improve CI visibility" changed_files=".github/scripts/validate-copilot-customizations.sh, .github/workflows/github-validate-copilot-customizations.yml" validation="bash -n scripts/*.sh; shellcheck -s bash scripts/*.sh; .github/scripts/validate-copilot-customizations.sh --scope root --mode strict" risk=Low links="Issue: N/A"`
- Expected output:
  - Full PR markdown body aligned with repository template.
  - `Changes` section with short bullets summarizing the real modifications.
  - `Validation` section containing commands and outcomes.
  - PR URL and confirmation that the PR body was updated (when tools are available).

## Validation
- Confirm all template-defined section headings are present and non-empty (or `N/A`).
- Confirm template checklist lines are present and intentionally marked.
- Confirm `Changes` bullets are brief and aligned with modified files.
- Confirm repository-specific scope or target fields are explicit when applicable.
- Confirm risk level and rollback plan are explicitly included.
- Confirm final PR body is persisted, not only generated as draft text.
