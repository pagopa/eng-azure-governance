---
description: Global defect-first Copilot code review baseline for repository changes.
applyTo: "**"
excludeAgent: "cloud-agent"
---

# Review Objective

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Find correctness bugs, security issues, regressions, and missing validation/tests before merge.
- Keep findings concise, severity-ordered, and tied to concrete file evidence.
- Prioritize: correctness, security, simplicity, maintainability.

## Required Output Shape

- Use severity buckets: `Critical`, `Major`, `Minor`, `Nit`, `Notes`.
- For each finding include: file/location, impact, and concrete fix guidance.
- Focus on actionable issues; avoid policy restatement without evidence.

## Required Checks

- Least privilege and no hardcoded secrets.
- Input validation, unsafe execution paths, and destructive behavior controls.
- Contract alignment with repository owners, validators, and active tests.
- Missing test coverage for changed behavior and missing docs for behavior changes.

## Review Discipline

- Do not rewrite large unaffected areas to satisfy style-only preferences.
- Escalate repeated anti-patterns (3+ occurrences in one diff) by one severity level.
- Prefer the smallest safe remediation that preserves requested behavior.
