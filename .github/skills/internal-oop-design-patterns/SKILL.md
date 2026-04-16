---
name: internal-oop-design-patterns
description: Use when refactoring object collaborations, replacing branching with polymorphism, decomposing god classes, isolating construction logic, or deciding whether an object-oriented design pattern is justified.
---

# Internal OOP Design Patterns

Use this skill as a decision and refactoring workflow, not as a mandate to add pattern ceremony. Start from the actual change pressure in the code and prefer the smallest design that removes the current problem.

## Workflow

1. Name the pressure before naming a pattern.
   Decide whether the problem is unstable construction, branching behavior, object collaboration, interface mismatch, lifecycle control, or oversized classes.
2. Prefer the lightest working shape.
   Keep a function, table, module, or small object when it solves the problem clearly. Introduce an interface or hierarchy only when there is a real variation point to protect.
3. Prefer composition and injected collaborators over inheritance.
   Use inheritance only when substitutability is real and the base abstraction earns its cost.
4. Refactor in behavior-preserving steps.
   Keep tests green, move one decision at a time, and stop once the change pressure is relieved.

## Default Selection Rules

- Reach for Strategy, State, or Command when variant behavior is growing and new cases are expected.
- Reach for Builder or Factory Method when object creation is unstable, repetitive, or difficult to validate at call sites.
- Reach for Adapter or Facade when boundary code is leaking foreign APIs into the rest of the system.
- Reach for Decorator when behavior must be layered dynamically without subclass explosion.
- Reach for Observer or Mediator only when direct coupling is the actual problem, not just because many objects exist.
- Treat Singleton as a last resort. Prefer dependency injection, explicit lifetime management, or module-level ownership first.

## References

- Load `references/pattern-selection.md` when you need a smell-to-pattern map with anti-triggers.
- Load `references/language-cues.md` when the language idioms should constrain how object-oriented the solution becomes.

## Guardrails

- Do not introduce a pattern only because its name matches the problem statement.
- Do not export pattern names in public APIs when domain terms would be clearer.
- Do not move stable branching into an abstract hierarchy unless new variants are expected.
- Do not add repositories, services, or managers as generic nouns without a concrete domain responsibility.
- Do not turn documentation into a workflow gate; follow the existing comment or docstring style instead of asking for a new global preference mid-task.

## Validation

- Run the existing tests before and after the refactor.
- Add or adjust tests only where the design change creates a new stable seam or protects behavior that was previously implicit.
