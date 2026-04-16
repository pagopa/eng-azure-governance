# GCP Operations Validation And Evidence

Use this reference when the base skill needs a deeper operational checklist.

## Preflight checklist

- confirm scope and rollout unit
- confirm rollback trigger and owner
- confirm monitoring, alerting, and logging signals for the affected surface
- confirm backup or recovery expectations when stateful services are involved
- confirm identity, Org Policy, and shared-network assumptions before widening rollout

## Rollout validation

- validate the first safe unit before widening scope
- check both success signals and unexpected deny, drift, or connectivity regressions
- record what was actually observed versus what was only expected

## Post-rollout evidence

- audit trail for what changed
- evidence that preventive controls still allow intended operations
- evidence that Cloud Monitoring and Cloud Logging still receive the expected signals
- evidence that inventory and reporting surfaces still describe the intended state
- evidence that restore or recovery assumptions were tested when relevant

## BC/DR note

BC/DR stays optional here as well.

Load it when the rollout affects continuity expectations, recovery posture, or business-critical platform capability.

## Monitoring and inventory evidence patterns

| Surface | Signals to check | What they confirm |
| --- | --- | --- |
| IAM or Org Policy rollout | Expected actions still succeed, denied actions are visible, audit records exist | The control still permits intended work and surfaces regressions |
| Shared VPC or topology change | Connectivity and logging still work for the scoped projects | The structure change did not silently break shared networking |
| Asset inventory and reporting | Inventory still shows the intended projects, identities, and control surfaces | The rollout did not create untracked drift |

## Backup versus restore proof expectations

| Need | Acceptable proof | Not enough on its own |
| --- | --- | --- |
| Backup posture exists | Protected resource inventory, policy attachment, recent backup success | A statement that backup is enabled |
| Restore is viable | Restore exercise, observed recovery time, integrity verification after recovery | Backup success without a restore test |
| DR posture is credible | Recovery workflow exercised for the scoped critical service or control plane | General health signals during normal operations |

## Stage-aware rollout evidence

| Rollout stage | Evidence to collect before widening |
| --- | --- |
| First folder or project set | Inheritance behaves as expected, monitoring is still present, rollback owner confirmed |
| First Shared VPC or central-service slice | Connectivity, audit logs, and ownership paths still behave as intended |
| Broad project or region expansion | Prior wave observations recorded, regressions investigated, escalation path confirmed |
