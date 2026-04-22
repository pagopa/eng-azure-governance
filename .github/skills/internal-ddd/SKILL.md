---
name: internal-ddd
description: Use when deciding whether a complex domain needs Domain-Driven Design, framing the current DDD stage from strategic modeling through tactical and evented patterns, and producing only the artifacts justified by real domain pressure.
---

# Internal DDD

Use this skill to decide how much Domain-Driven Design a problem deserves, then produce only the artifacts needed for the current stage and the next adjacent lane.

## When to use

- Complex or fast-changing business rules are colliding with implementation structure.
- Teams or services are disagreeing on terms, ownership, or domain boundaries.
- Integration seams are unstable and the domain language is drifting between contexts.
- Auditability, invariants, or workflow coordination make tactical or evented modeling worth evaluating.

## When not to use

- Simple CRUD with stable rules and obvious ownership.
- Localized bug fixes, isolated refactors, or framework-only questions.
- Cases where no domain knowledge or proxy product expertise is available.

## Workflow

1. Run a DDD viability check.
   Confirm at least two signals: domain volatility, model collisions, unstable boundaries, or critical invariants.
2. Start with the strategic frame unless the boundaries are already stable.
   Name subdomains, bounded contexts, language, and translation seams before escalating into tactical or evented modeling.
3. Choose the working mode.
   Use strategic mode for subdomains and bounded contexts, tactical mode for aggregates and invariants, and evented mode only when integration or workflow pressure justifies it.
4. Produce only the smallest useful artifact set.
   Avoid generating strategic, tactical, and evented deliverables all at once.
5. Record evidence, success criteria, and the next owner.
   End with what was decided, what remains risky, and which adjacent skill or engineering lane should act next.

## Working modes

- Strategic: subdomain map, bounded contexts, ubiquitous language, boundary ADRs, and cross-context translation seams.
- Tactical: aggregates, value objects, domain services, repository contracts, and invariants inside a stable bounded context.
- Evented: commands, domain events, read models or projections, CQRS rationale, saga boundaries, and rebuild or versioning policy.

## Pressure map

- Boundary and terminology collisions: stay strategic until context ownership and translation seams are explicit.
- Weak invariants inside one context: use tactical modeling to decide aggregate boundaries, value objects, and enforcement homes.
- Read-write separation, read models, or long-running workflows: treat them as evented candidates only when operational pressure is explicit.
- Event history as source of truth: justify it separately from general event publication; it is a higher-cost choice than simple domain events.

## Adjacent lanes

- Use `internal-change-impact-analysis` when the challenge is incremental adoption inside an existing system.
- Use `internal-oop-design-patterns` when a tactical model now needs implementation-level pattern choices.
- Use `antigravity-api-design-principles` when bounded-context seams are turning into API or contract design work.
- Treat infrastructure boundaries as legitimate bounded-context candidates when the real seams are module ownership, environment contracts, or repo-level responsibility lines rather than object-oriented code.
- Keep evented design inside this skill until the rationale, ownership, and operational cost are explicit enough to hand off safely.

## References

- Load `references/mode-selection.md` when deciding whether the work is strategic, tactical, or evented.
- Load `references/ddd-deliverables.md` when you need the concrete artifact checklist and exit criteria.

## Output requirements

Always return:

- domain pressure and assumptions
- selected DDD mode and why
- artifacts produced or required next
- success criteria or evidence captured for the current stage
- explicit anti-overengineering note when DDD is not justified
- open risks and next recommended lane

## Guardrails

- Do not present this skill as a router; it is a decision and artifact workflow.
- Do not recommend CQRS, event sourcing, or sagas without a clear pressure from workflow complexity or integration boundaries.
- Do not recommend read-write separation, event history as source of truth, or read models unless the operational reason is explicit.
- Do not let DDD vocabulary replace concrete domain terms.
