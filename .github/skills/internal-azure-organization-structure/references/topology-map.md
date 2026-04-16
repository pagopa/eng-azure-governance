# Azure Organization Structure Topology Map

Use this reference when turning a structural Azure question into the right control surface.

## Core boundary

- **Tenant and management-group hierarchy**: own enterprise segmentation, policy inheritance scope, and landing-zone grouping.
- **Subscriptions**: own workload, platform, environment, or residency placement boundaries.
- **Landing zones**: package platform capabilities, connectivity, and operating-model expectations.
- **Platform network topology**: decide hub-spoke, Virtual WAN, private connectivity, and regional placement at layout level.

## Default review checklist

1. Is this a structure choice, a governance control, or an operations concern?
2. Does the capability belong at tenant, management-group, subscription, or landing-zone level?
3. Is the change shaping layout, shaping permissions, or validating a rollout?
4. What is the smallest safe rollout unit: one management group, one subscription set, or one region set?
5. What must be validated before broad rollout?
6. What is the rollback path if connectivity, policy inheritance, or platform automation breaks?

## Common structural mappings

| Need | Use first | Notes |
| --- | --- | --- |
| Separate platform ownership from workload ownership | management-group plus subscription model | Keep landing-zone scope explicit |
| Standardize shared connectivity | platform-level topology choice | Keep routing and region placement visible |
| Segment environments or regulatory boundaries | subscription purpose plus hierarchy placement | Do not hide residency assumptions |
| Place shared services or platform controls | landing-zone placement | Keep governance logic separate |
| Roll out baseline structure safely | rollout unit definition | Validate one safe unit before widening |

## Important Azure-specific reminders

- Management groups shape policy and RBAC inheritance scope, but they do not replace subscription-level ownership.
- Landing-zone design should keep platform topology separate from workload-by-workload implementation detail.
- Regional placement is a structural concern when it changes connectivity, sovereignty, or continuity assumptions.

## Starter management-group and subscription patterns

| Pattern | When it fits | Watch for |
| --- | --- | --- |
| Platform MG plus workload MG split | A central platform team needs clear separation from application ownership | Do not hide production versus non-production risk boundaries inside one flat workload group |
| Environment-first subscription families | Teams share controls and rollout cadence by environment | Keep environment naming aligned to operating reality, not only to billing labels |
| Regulated or sovereign segment | A subset of workloads needs distinct residency, approval, or connectivity posture | Keep the segment requirement explicit so it does not become a vague exception bucket |
| Shared connectivity and management subscriptions | Platform services need stable ownership outside workload subscriptions | Keep service purpose and landing-zone expectations explicit |

## Landing-zone placement heuristics

| Question | Prefer | Reason |
| --- | --- | --- |
| Does the capability provide shared connectivity or central policy plumbing? | Platform landing zone or dedicated platform subscription | Keeps shared controls separate from workload delivery |
| Does the capability exist only for one workload or product boundary? | Workload landing zone or workload subscription | Avoids centralizing application-specific ownership |
| Does residency or regulated access change the operating model? | Dedicated hierarchy or landing-zone segment | Prevents mixing incompatible policy and connectivity assumptions |
| Does the change affect many subscriptions at once? | Management-group level placement with staged rollout | Keeps inheritance and blast radius visible |

## Safe rollout-unit examples

| Structural change | Start with | Widen after |
| --- | --- | --- |
| New management-group branch | One low-risk subscription family | Inheritance, policy scope, and operational ownership are confirmed |
| Landing-zone baseline update | One landing zone or one environment slice | Connectivity, automation, and rollback behavior are observed |
| Platform subscription introduction | One shared capability with named consumers | Ownership, routing, and dependency impact are validated |
| Region or residency split | One workload set with explicit fallback | Connectivity, sovereignty controls, and continuity assumptions are proven |
