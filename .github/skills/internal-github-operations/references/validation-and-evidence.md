# GitHub Operations Validation And Evidence

Use this reference when the base skill needs a deeper operational checklist.

## Preflight checklist

- confirm scope and rollout unit
- confirm rollback trigger and owner
- confirm runner, workflow, and audit signals for the affected surface
- confirm permission and environment assumptions before widening rollout
- confirm reporting or export surfaces needed for follow-up evidence

## Rollout validation

- validate the first safe unit before widening scope
- check both success signals and unexpected permission, runner, or release regressions
- record what was actually observed versus what was only expected

## Post-rollout evidence

- audit trail for what changed
- evidence that intended workflows still run with the expected permissions
- evidence that runner capacity and health still match the operating assumptions
- evidence that audit or reporting surfaces still describe the intended state

## Continuity note

Continuity stays optional here as well.

Load it when the rollout affects build, release, or repository continuity expectations.

## Runner health evidence patterns

| Surface | Signals to check | What they confirm |
| --- | --- | --- |
| Hosted or self-hosted runner rollout | Queue time, runner availability, job execution success, failed startup or registration events | Runner capacity and health still match the operating assumptions |
| Environment or protected deployment path | Approval flow, environment access, deployment job outcome | Release controls still allow intended delivery |
| Repository or org workflow change | Workflow run outcome, token scope behavior, audit events | The rollout did not silently widen or break automation behavior |

## Workflow-permission validation

| Need | Acceptable proof | Not enough on its own |
| --- | --- | --- |
| Workflow still has the intended permissions | Successful expected action plus evidence that denied actions remain denied | A single green run without checking token scope |
| Environment controls still work | Approval, secret access, and deployment path behave as designed | Deployment success without confirming who could trigger it |
| Automation trust is still constrained | Audit records plus scoped actor behavior match the design | The absence of visible failures |

## Audit and drift follow-up patterns

| Rollout stage | Evidence to collect before widening |
| --- | --- |
| First repository or environment | Audit trail exists, permission behavior matches expectation, rollback owner confirmed |
| First runner group or automation boundary | Queue health, registration health, and failure handling still work |
| Broad organization rollout | Prior wave observations recorded, drift checks reviewed, regressions investigated |
