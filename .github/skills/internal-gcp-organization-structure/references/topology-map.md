# GCP Organization Structure Topology Map

Use this reference when turning a structural GCP question into the right control surface.

## Core boundary

- **Org and folder hierarchy**: own enterprise segmentation, policy inheritance scope, and operating-boundary grouping.
- **Billing accounts**: own financial responsibility and chargeback alignment.
- **Projects**: own workload, platform, environment, or residency placement boundaries.
- **Shared VPC topology**: decide host and service project placement plus network ownership at layout level.

## Default review checklist

1. Is this a structure choice, a governance control, or an operations concern?
2. Does the capability belong at org, folder, billing, project, or Shared VPC host level?
3. Is the change shaping layout, shaping permissions, or validating a rollout?
4. What is the smallest safe rollout unit: one folder, one project set, or one region set?
5. What must be validated before broad rollout?
6. What is the rollback path if networking, policy inheritance, or platform automation breaks?

## Common structural mappings

| Need | Use first | Notes |
| --- | --- | --- |
| Separate platform ownership from workload ownership | folder plus project model | Keep Shared VPC ownership explicit |
| Standardize shared connectivity | Shared VPC topology choice | Keep host and service project boundaries visible |
| Segment environments or regulatory boundaries | project purpose plus hierarchy placement | Do not hide residency assumptions |
| Split finance ownership from platform execution | billing-account model | Make the ownership model explicit |
| Roll out baseline structure safely | rollout unit definition | Validate one safe unit before widening |

## Important GCP-specific reminders

- Org and folder hierarchy shape policy inheritance scope, but they do not replace project-level ownership.
- Shared VPC is a structure decision first; IAM and firewall posture come later in governance.
- Regional placement is a structural concern when it changes connectivity, sovereignty, or continuity assumptions.

## Starter folder and project patterns

| Pattern | When it fits | Watch for |
| --- | --- | --- |
| Platform folder plus workload folders | A central platform team needs clear separation from product teams | Do not hide environment or residency differences inside one flat workload folder |
| Environment-first project families | Teams share controls and rollout cadence by environment | Keep the project purpose explicit so billing and operations remain clear |
| Regulated workload segment | A subset of projects needs stronger residency or approval posture | Keep the regulated segment justified by requirements, not vague exception status |
| Shared services projects separate from application projects | Platform services need stable ownership outside product delivery | Name which shared capabilities belong there and which do not |

## Shared VPC placement heuristics

| Question | Prefer | Reason |
| --- | --- | --- |
| Does the network serve many workloads across one operating boundary? | Central host project with named service projects | Keeps network ownership clear while preserving workload project ownership |
| Does the workload need isolated network administration for regulation or autonomy? | Dedicated host project or separate topology segment | Avoids forcing incompatible controls into one network boundary |
| Does the change affect many projects at once? | Folder-level rollout and one low-risk service-project set first | Keeps inheritance and blast radius visible |
| Does the host project also carry platform services? | Separate network and shared-service ownership unless clearly justified | Prevents one project from becoming the default home for everything |

## Billing ownership examples

| Situation | Useful pattern | Review note |
| --- | --- | --- |
| Central platform funds shared controls | Billing ownership separate from workload project ownership | Make chargeback or showback assumptions explicit |
| Business units own spend but share core network | Business-unit project ownership plus central Shared VPC service | Keep the dependency and support model explicit |
| Regulated workloads need isolated financial reporting | Dedicated billing boundary or reporting model | Do not let compliance segmentation drift from actual ownership |

## Safe rollout-unit examples

| Structural change | Start with | Widen after |
| --- | --- | --- |
| New folder branch | One low-risk project family | Inheritance, automation, and rollback behavior are confirmed |
| Shared VPC introduction | One host project with one low-risk service-project set | Connectivity, logging, and ownership paths are proven |
| Billing ownership realignment | One product or environment slice | Chargeback, approvals, and automation still behave as intended |
| Region or residency split | One workload set with explicit fallback | Connectivity and sovereignty assumptions are validated |
