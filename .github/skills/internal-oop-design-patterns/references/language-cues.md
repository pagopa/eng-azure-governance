# Language and Documentation Cues

Load this file when a pattern seems plausible but the host language should influence how heavy the solution becomes.

## Java and C#

- Interfaces and explicit dependency injection are cheap when the variation point is real.
- Prefer records or small immutable types for data carriers where the codebase already uses them.
- Avoid inheritance trees built only for test doubles or code sharing.

## TypeScript and JavaScript

- Prefer plain objects, closures, and discriminated unions before introducing class-heavy hierarchies.
- Treat framework decorators and GoF Decorator as different concepts; do not conflate them.
- Reach for classes when lifecycle, encapsulated state, or framework integration genuinely benefits from them.

## Python

- Prefer small objects, callables, protocols, or dataclasses before porting Java-style class hierarchies.
- Use explicit composition and duck typing freely when they keep the design simpler.
- Follow the existing docstring style in nearby files; do not stop the workflow to ask for a global documentation preference unless the user explicitly requested documentation standards work.

## Naming and Comments

- Name abstractions after domain behavior, not after the pattern, unless the pattern name materially improves clarity.
- Add intent comments only when the chosen seam would not be obvious to the next maintainer.
- Keep SOLID as a pressure test, not as a checklist that every class must visibly satisfy.
