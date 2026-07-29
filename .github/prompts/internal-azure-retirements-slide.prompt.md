---
name: internal-azure-retirements-slide
agent: "agent"
description: "Generate or validate the canonical monthly Azure retirements slide TSV from an existing aggregate TSV without live Azure collection"
argument-hint: "Required year and month (YYYY-MM); optional export root when the aggregate is outside the default repository path"
---

<!-- markdownlint-disable-file MD041 -->

Requested period:
${input:period:Required year and month in YYYY-MM format}

Optional export root:
${input:output_root:Leave empty to use src/comitato/comitato_azure_retirements/exports}

## Instructions

1. Use
   [.github/skills/local-azure-retirements/SKILL.md](../skills/local-azure-retirements/SKILL.md)
   as the controlling workflow.
2. Resolve the requested period exactly. Do not substitute the newest available
   export.
3. Confirm that the monthly aggregate TSV exists and contains data rows.
4. Run only the canonical slide stage without live Azure collection.
5. Stop and report the exact diagnostic if the input or traceability checks
   fail.

## Validation

- Confirm the exact ordered output header.
- Confirm deterministic sorting and link fallback.
- Confirm platform/subscription JSON preservation.
- Report the slide path, row counts, and any remaining diagnostic error.

## Minimal example

Input:

```text
period: 2026-07
output_root:
```

Expected behavior: reuse the July aggregate under the default export root,
generate the July slide TSV through the slide-only workflow, and report its
validation result without calling Azure APIs.
