# GitHub.com Copilot Code Review

This file is only for GitHub.com Copilot code review.

It is not a general task-execution guide, repository routing guide, planning
workflow, or local agent runtime contract.

## Review Objective

Review changed files for defects that matter before merge.

- Prioritize correctness, security, regressions, missing validation, and
  maintainability.
- Prefer actionable findings over broad advice.
- Tie each finding to concrete changed-file evidence.
- Do not restate repository policy unless the diff creates a specific risk.

## Finding Priority

Use these buckets when reporting issues:

- `Critical`: data loss, credential exposure, remote code execution, production
  outage, or a merge-blocking contract break.
- `Major`: correctness bugs, security weaknesses, broken validators, missing
  required tests, or behavior regressions.
- `Minor`: maintainability, edge-case, resilience, or observability issues that
  should be fixed before merge when practical.
- `Nit`: small clarity or style issues that are safe to ignore.
- `Notes`: useful context that is not a defect.

## Required Checks

- Check for hardcoded secrets, credentials, keys, tokens, and tenant-sensitive
  values.
- Check least privilege, destructive behavior controls, unsafe execution paths,
  and missing input validation.
- Check whether changed behavior has appropriate tests, fixtures, docs, or
  validators.
- Check contract alignment for changed schemas, generated assets, sync behavior,
  prompts, instructions, skills, scripts, and CI workflows.
- Check that fixes are scoped to the requested behavior and do not rewrite large
  unaffected areas.

## Review Discipline

- Report findings first, ordered by severity.
- For each finding, include the file or changed area, impact, and a concrete fix
  direction.
- Avoid speculative findings when the diff does not provide enough evidence.
- Avoid praise, summaries, or style-only comments unless they reveal a real
  maintenance risk.
- Escalate repeated instances of the same defect pattern when the repetition
  increases risk.

## Non-Scope

- Do not provide implementation plans unless the review finding needs fix
  guidance.
- Do not ask the author to follow local runtime workflows that GitHub.com cannot
  execute.
- Do not treat this file as instructions for coding agents, local CLIs, or
  non-review Copilot chat behavior.
