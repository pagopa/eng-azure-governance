---
name: internal-github-actions
description: Use when authoring or revising GitHub Actions workflows, reusable workflows, or deciding when shared step logic should move into a composite action.
---

# GitHub Actions Skill

## When to use
- Create or modify GitHub Actions workflows under `.github/workflows/`.
- Create or modify reusable workflows exposed through `workflow_call`.
- Decide whether repeated step logic should stay inline, move to a reusable workflow, or move to a composite action.
- Add CI/CD jobs such as build, test, lint, release, or deployment.
- Review whether a workflow should stay inline, move to `workflow_call`, or extract script-first logic before introducing another reusable layer.

Use `internal-devops-core-principles` when the question is delivery strategy, release model, or operating-model health rather than workflow authoring.

## Mandatory rules
- Follow `.github/instructions/internal-github-actions.instructions.md`.
- Prefer OIDC for cloud authentication.
- Pin every third-party action to a full-length SHA with adjacent release comment.
- Keep `permissions` least-privilege.
- Keep step names and logs in English.
- Read GitHub's official workflow syntax and context-availability documentation before making or validating changes that depend on expression scope, context usage, or key-specific rules; do not rely on memory.
- Validate `workflow_dispatch` free-form inputs before shell or deploy steps consume them.

## Reference map

- Load [auth snippets](references/auth-snippets.md) for AWS, Azure, and GCP OIDC examples.
- Load [workflow example](references/workflow-example.md) for a compact validated deploy archetype.
- Load [reusable workflow template](references/reusable-workflow-template.md) when the repeated unit is one or more jobs.
- Load [workflow patterns catalog](references/workflow-patterns-catalog.md) for matrix, scheduled, environment-gated, and reusable-workflow shapes.
- Load [caching and artifacts](references/caching-and-artifacts.md) for deterministic cache keys and reviewed artifact handoffs.
- Load [reuse decision tree](references/reuse-decision-tree.md) when inline steps, scripts, reusable workflows, and composite actions all look plausible.
- Load [security hardening checklist](references/security-hardening-checklist.md) when the workflow touches deployment, secrets, self-hosted runners, or untrusted events.
- Load `.github/skills/internal-github-action-composite/SKILL.md` when the reusable unit becomes step-level or contract-sensitive.

## Choose the right reuse pattern

| Situation | Pattern |
|---|---|
| Simple pipeline in one repository | Standard workflow |
| Repeated job orchestration inside one repository | Reusable workflow (`workflow_call`) |
| Shared step logic across repositories or many workflows | Composite action |
| Mostly shell or language-specific commands with thin orchestration | Script called from the workflow |
| Composite action authoring or contract changes | Load `internal-github-action-composite` |

## Common mistakes

| Mistake | Why it matters | Instead |
|---|---|---|
| Using `permissions: write-all` or omitting permissions entirely | Grants the token maximum access and widens the blast radius of a compromised step | Declare only the permissions the job needs |
| Pinning actions by tag (`@v4`) instead of SHA | Tags are mutable and can be retargeted upstream | Pin to a full-length commit SHA with a release comment |
| Long-lived cloud credentials in secrets instead of OIDC | Static credentials can leak and do not expire automatically | Configure OIDC federation for AWS, Azure, or GCP |
| Missing `environment` protection on production deploys | Anyone who can push to the branch can deploy to production | Add an environment with required reviewers |
| Letting `workflow_dispatch` inputs flow directly into shell or deploy steps | Free-form input becomes a control path without validation | Validate and normalize inputs in an early step or job |
| Using `runner.temp` or other runner-scoped contexts in workflow-root `env` or `jobs.<job_id>.env` | The workflow fails validation before it even queues | Use `runner` only in keys that allow it, or derive the path from runner environment variables inside `run` |
| Treating a cache miss or restore notice as the failing condition | You stop at an informational setup line and fix the wrong thing | Find the first failed step and confirm whether the action can actually fail on that message |
| Using timestamp-driven or branch-only cache keys | Cache hits become noisy, stale, or misleading across runs | Key caches from lockfiles, tool versions, and other stable inputs |
| Uploading artifacts without explicit name or retention | Review and deploy handoffs become ambiguous and harder to clean up | Name artifacts deliberately and set `retention-days` |
| Duplicating steps across workflows instead of reusable workflow or composite action | Maintenance burden grows with every copy | Extract to a reusable workflow in one repo or a composite action across repos |

## Cross-references

- **internal-github-action-composite** (`.github/skills/internal-github-action-composite/SKILL.md`): for composite-action authoring and compatibility-sensitive contract changes.
- **internal-terraform** (`.github/skills/internal-terraform/SKILL.md`): for the Terraform resources deployed by CI/CD.

## Checklist

- [ ] OIDC configured for cloud auth.
- [ ] All third-party actions pinned by full SHA with release comments.
- [ ] `permissions` minimized per job.
- [ ] `workflow_dispatch` inputs validated before shell, deploy, or infrastructure steps use them.
- [ ] Context usage matches GitHub's context-availability rules for the specific workflow keys involved.
- [ ] Cache keys are deterministic and artifacts set explicit `retention-days` when they bridge jobs.
- [ ] Environment protection and `concurrency` are enabled for production deploys.
- [ ] Self-hosted runner use is justified and scoped.
- [ ] The reuse choice has been checked against `references/reuse-decision-tree.md`.

## Validation

- `actionlint` on workflow files, if available.
- When expressions use non-global contexts, compare each workflow key against GitHub's official context-availability table.
- For CI-log debugging, verify the first failed step before treating earlier cache or setup lines as causal.
- Verify there is no `permissions: write-all` and no missing permissions block where least privilege matters.
- Verify all third-party `uses:` lines reference full SHAs instead of tags.
- Re-check that every referenced local guide resolves before treating the skill update as complete.
