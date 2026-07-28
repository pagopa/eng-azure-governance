---
description: Makefile conventions for deterministic targets, readable recipes, and explicit phony declarations.
applyTo: "**/Makefile,**/*.mk"
excludeAgent: "cloud-agent"
---

# Makefile Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Use the bundle checker and distinguish its `phonydeclared` finding from
  review-only Make behavior.
- Check target prerequisites, recipe prefix characters, `.PHONY`, variables,
  and `$ / $$` expansion intent.
- Review order-only prerequisites, parallelism, recursive Make, and shared
  artifacts when target ordering or concurrency matters.
- Separately review deterministic build order, hidden environment coupling,
  failure behavior, and undocumented side effects when the changed file
  provides evidence.
- Treat shell semantics and domain behavior as human review concerns; the
  checker never invokes recipes.
- Remember that `make -n` is not a generic safety boundary: recipes may still
  have observable expansion or tool-specific behavior.
