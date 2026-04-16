# Analysis Dimensions — Detailed Checklists

## 1. Correctness analysis
- Does the code do what the change claims?
- Are edge cases handled?
- Are error paths tested?
- Is input validation present and sufficient?
- Do return types match caller expectations?
- Are concurrency assumptions safe?

## 2. Separation of concerns

| Principle | What to check |
|---|---|
| Business vs I/O | Is business logic cleanly separated from I/O, SDKs, and persistence? |
| Module boundaries | Are module boundaries clear and cohesive? |
| Naming clarity | Do names reflect what the code does in business terms? |
| Dependency direction | Do high-level modules avoid depending on low-level details? |
| Interface stability | Are module contracts (inputs/outputs) stable and documented? |

## 3. Architecture

| Quality | What to check |
|---|---|
| Separation of concerns | Are business logic, I/O, and presentation layers distinct? |
| Dependency direction | Do dependencies point inward (infrastructure → application → core logic)? |
| Coupling | Is coupling between modules explicit and minimal? |
| Cohesion | Are related concepts grouped together? |
| Extensibility | Can this design accommodate likely future changes without significant rework? |
| Testability | Can each component be tested in isolation? |
| Operational readiness | Are logs, metrics, and health checks present for production visibility? |

## 4. Blind-spot detection

Apply lateral thinking on each dimension:

- **Temporal analysis**: Will this change cause problems at scale? After 6 months of accumulation?
- **Team dynamics**: Does this change increase onboarding friction for new team members?
- **Cross-service impact**: Could this change break consumers or upstream producers?
- **Operational burden**: What happens when this fails at 3 AM? Can on-call engineers debug it?
- **Data implications**: Are there schema changes, migration needs, or data consistency risks?
- **Security surface**: Does this change expand the attack surface?
- **Performance cliffs**: Is there a hidden O(n²) or unbounded resource consumption?
- **Configuration drift**: Are there environment-specific assumptions that break in other stages?
- **Missing observability**: Can we know if something goes wrong after deployment?
- **Alternative solutions**: Is there a fundamentally simpler approach that was not considered?
