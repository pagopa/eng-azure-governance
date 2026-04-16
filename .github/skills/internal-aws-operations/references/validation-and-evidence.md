# AWS Operations Validation And Evidence

Use this reference when the base skill needs a deeper operational checklist.

## Preflight checklist

- confirm scope and rollout unit
- confirm rollback trigger and owner
- confirm IAM assumptions with safe simulation when relevant
- confirm logging and alerting signals for the affected surface
- confirm backup or recovery expectations when stateful services are involved

## Rollout validation

- validate the first safe unit before widening scope
- check both success signals and unexpected deny or access regressions
- record what was actually observed versus what was only expected

## Post-rollout evidence

- audit trail for what changed
- evidence that preventive controls still allow intended operations
- evidence that central logging or monitoring still receives data
- evidence that restore or recovery assumptions were tested when relevant

## BC/DR note

BC/DR stays optional here as well.

Load it when the rollout affects continuity expectations, recovery posture, or business-critical platform capability.

## Preflight evidence by rollout stage

| Rollout stage | Evidence to collect before widening |
| --- | --- |
| First account or first OU | IAM simulation or access check, logging still arriving, automation still able to deploy or operate |
| Delegated admin or shared-service activation | Service ownership confirmed, central logs visible, failure path and rollback owner confirmed |
| Broad OU or region expansion | Prior wave observations recorded, unexpected denies investigated, alerting and escalation path confirmed |

## Backup versus restore proof patterns

| Need | Acceptable proof | Not enough on its own |
| --- | --- | --- |
| Backup posture exists | Scheduled backups, retention policy, backup job success, protected resource inventory | A statement that backup is enabled |
| Restore is viable | Recent restore test, recovery time observed, application or data integrity verified | Backup job success without a restore exercise |
| DR assumptions are credible | Recovery workflow exercised for the scoped critical service or control plane | Monitoring green after normal operations |

## AWS signals that confirm intended state

| Surface | Signals to check | What they confirm |
| --- | --- | --- |
| Access and governance rollout | CloudTrail events, policy simulation result, expected role assumption path | The control still permits intended operations and records who used it |
| Configuration posture | AWS Config evaluations, conformance-pack state, remediation outcome | Preventive and detective controls still align with the intended baseline |
| Logging and observability | Central log delivery, CloudWatch alarms, service health or metric continuity | The rollout did not break visibility on the affected surface |
| Recovery posture | Backup job history, restore test output, runbook execution notes | The stated recovery assumption has real evidence behind it |
