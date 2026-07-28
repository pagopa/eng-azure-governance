---
description: Java project standards with DDD boundaries, readability-first design, and deterministic unit testing.
applyTo: "**/*.java,**/pom.xml,**/build.gradle,**/build.gradle.kts"
excludeAgent: "cloud-agent"
---

# Java Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify domain boundaries remain clear and business logic is not leaked into adapters.
- Flag null-safety and exception-handling gaps that can cause runtime faults.
- Check changed APIs for backward-compatibility impact and contract drift.
- Verify tests are deterministic and cover behavior changes, not only happy paths.
- Report dependency changes that widen attack surface or duplicate transitive libs.
- Check build metadata for reproducibility and version pin hygiene.
- Flag excessive complexity, deep nesting, or unreadable control flow.
