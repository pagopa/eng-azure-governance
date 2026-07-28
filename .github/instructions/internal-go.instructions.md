---
description: Instructions for writing Go code following idiomatic Go practices and community standards
applyTo: "**/*.go,**/go.mod,**/go.sum"
excludeAgent: "cloud-agent"
---

# Go Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Verify error handling is explicit and no critical errors are silently ignored.
- Flag context misuse in I/O or network paths that can leak goroutines.
- Check exported APIs for clear contracts, naming, and package boundaries.
- Verify tests cover changed behavior and avoid flaky timing assumptions.
- Report data races, shared-state hazards, or unsafe concurrency patterns.
- Check dependency updates in `go.mod` and `go.sum` for unnecessary scope creep.
- Flag logging or panic usage that can expose sensitive operational details.
