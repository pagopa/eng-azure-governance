---
name: internal-devops-core-principles
description: Use when the task is about delivery-system strategy, release safety, operational readiness, or incident learning across the software-delivery lifecycle, not one-off workflow syntax or provider commands.
---

# Internal DevOps Core Principles

Use this skill for end-to-end delivery-system thinking, not for one-off YAML syntax questions or provider-specific command lookup.

## When to use

- The task is about delivery-system strategy, release safety, operational readiness, or incident learning across the software-delivery lifecycle.
- The main need is DevOps tradeoff framing rather than one-off workflow syntax or provider commands.
- A repository or platform decision must be evaluated through CALMS, DORA, rollout safety, or operational controls.

## Core Lens

Apply CALMS in this order:

1. Culture: shared ownership, blameless learning, clear handoffs.
2. Automation: remove repetitive human gates.
3. Lean: reduce queue time, handoffs, and batch size.
4. Measurement: use DORA and operational metrics.
5. Sharing: document runbooks, incidents, and patterns.

## Infinity Loop Scope

Always identify which parts of the DevOps loop are actually in play:

- Plan: requirements, acceptance criteria, risks, success metrics, and infrastructure or deployment needs.
- Code: reviewable change size, team conventions, dependency discipline, and tests written with the change.
- Build: reproducible builds, locked dependencies, artifact versioning, build speed, and vulnerability scanning.
- Test: automated unit, integration, end-to-end, performance, and security checks with clear pass or fail gates.
- Release: release contents, versioning, changelog or release-note hygiene, approvals proportional to risk, and rollback readiness.
- Deploy: infrastructure as code, progressive rollout strategy, deployment verification, blast-radius control, and rollback automation.
- Operate: incident response, runbooks, SLO ownership, capacity planning, configuration hygiene, patching, backups, and disaster recovery.
- Monitor: actionable metrics, logs, traces, alerts, DORA, SLI and SLO signals, plus business feedback that loops back into planning.

## Delivery Rules

- Prefer small, frequent, reversible changes.
- Optimize for lead time and mean time to recovery, not ceremony.
- Use automated checks as the default quality gate.
- Keep code, infrastructure, environments, builds, tests, releases, and deployments reproducible.
- Design rollouts for rollback, not just for first success.
- Prefer progressive delivery, feature flags, or other blast-radius controls over all-at-once production changes.
- Treat observability and incident readiness as delivery requirements, not as post-deploy chores.
- Use approvals only when they reduce measurable risk that automation cannot already cover.

## DORA Focus

Always consider:

- Deployment frequency
- Lead time for changes
- Change failure rate
- Mean time to recovery

If a workflow harms one of these, call it out explicitly.

## Minimum Operational Controls

Good DevOps guidance should usually account for these controls when relevant:

- CI that gives fast, actionable feedback on every meaningful change.
- Test layers that are automated, repeatable, and not flaky by default.
- Security scanning and dependency hygiene inside the delivery path.
- Release discipline with clear contents, auditability, and rollback preparation.
- Deployment verification instead of assuming success after the pipeline turns green.
- Runbooks, alert ownership, and an incident path that people can actually execute.
- SLI, SLO, and DORA visibility that influences the next planning cycle.

## What Good Looks Like

- Fast feedback in pull requests and CI.
- Clear ownership from commit to production.
- Builds that work from a clean checkout and produce versioned artifacts.
- Observable systems with actionable alerts, useful logs, and correlatable traces.
- Release pipelines that are testable, repeatable, and reversible.
- Post-incident learning that changes the system, not only the document.

## Anti-Patterns

- Large release trains as the default.
- Manual copy-paste deployments.
- Green pipelines with no deployment verification or rollback rehearsal.
- Monitoring that creates noisy alerts with no operator action tied to them.
- Hidden release knowledge, on-call knowledge, or recovery steps.
- Approval chains with no measurable risk reduction.
- Treating DevOps as a team name instead of an operating model.

## Output Expectations

When giving guidance:

- State which Infinity Loop phases plus CALMS and DORA concerns apply.
- Identify the current bottleneck.
- Identify missing controls in testing, release safety, deployment safety, operations, or observability when they matter.
- Recommend the minimum process and automation changes that improve flow.
