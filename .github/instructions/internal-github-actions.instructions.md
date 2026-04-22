---
description: Baseline standards for GitHub Actions workflows and composite actions with SHA pinning, least privilege, and deterministic execution.
applyTo: "**/workflows/**,**/actions/**/action.y*ml"
---

# GitHub Actions Instructions

## Security baseline

- Prefer OIDC over long-lived secrets.
- Pin actions to full-length commit SHAs with adjacent release comments and upstream release URLs.
- Pin `docker://` references and workflow container images by digest.
- When an image is pinned by digest, keep the human-readable tag or version in an adjacent comment or nearby reference.
- Keep `permissions` minimal.
- Start with `contents: read` and add write scopes only when the job requires them.
- Avoid `pull_request_target` for untrusted code.
- Pass secrets only through `secrets.*` or protected environments; never hardcode them in `env`.
- For production deployments, use protected `environment:` gates with required reviewers instead of relying on branch conditions alone.
- Treat self-hosted runners as trusted infrastructure and scope them to the repositories, runner groups, and network access they actually need.

## Family baseline

- Use clear English step names and deterministic outputs.
- Set explicit `timeout-minutes` for workflows that could otherwise hang.
- Set `concurrency` when jobs can conflict on a shared target.
- Prefer reusable workflows (`workflow_call`) for repeated job orchestration inside one repository.
- Prefer smaller jobs with explicit `needs` over monolithic workflows when phases are logically separate.
- Use `if` conditions deliberately for branch, event, and environment-specific execution.
- Before making or validating workflow changes that depend on expression scope, context usage, or key-specific rules, read GitHub's official workflow syntax and context-availability documentation; do not rely on memory.
- The `inputs` context is only available in reusable workflows or `workflow_dispatch` runs. Workflows that also run on `push` or `pull_request` must not rely on shared `inputs.*` expressions for workflow-root `env`, job `env`, or cache keys.
- Do not place runner-derived paths such as `runner.temp` in workflow-root `env` or `jobs.<job_id>.env`; resolve them in step-level keys that allow `runner`, or derive them from default runner environment variables inside `run`.
- Treat IDE, parser, `actionlint`, and queue-time errors such as `Unrecognized named-value` as mandatory documentation-check triggers.
- When debugging workflow logs, identify the first failed step before treating an earlier cache or setup line as the root cause; cache misses are informational unless the action or workflow explicitly makes them fatal.
- Keep cache keys deterministic from lockfiles, tool versions, or other stable inputs instead of timestamps or branch-only entropy.
- Set explicit artifact `retention-days` when artifacts bridge review, release, or deploy stages.
- Validate `workflow_dispatch` free-form inputs before shell, deploy, or infrastructure steps consume them.
- Path-specific instructions can use `excludeAgent: "code-review"` or `excludeAgent: "cloud-agent"` when workflow guidance must be scoped to one GitHub Copilot surface, but treat that as a deliberate optimization rather than a default requirement.

## Use the skill for deeper guidance

- Load `.github/skills/internal-github-actions/SKILL.md` for workflow-vs-reusable-vs-composite decisions, reusable workflow templates, cache and artifact patterns, and workflow hardening checklists.
- Keep this instruction lean because it is part of the source-managed baseline mirrored into consumer repositories; add new always-on GitHub Actions depth only when downstream reuse justifies that sync cost, and keep advanced patterns, examples, and decision support in the skill references.
- Keep this instruction as the auto-loaded baseline; keep authoring depth and examples in the skill.
