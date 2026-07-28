---
description: JSON formatting and consistency standards for registry and configuration data files.
applyTo: "**/authorizations/**/*.json,**/organization/**/*.json,**/src/**/*.json,**/data/**/*.json"
excludeAgent: "cloud-agent"
---

# JSON Review Checks

This file is optimized for Copilot code review and should produce only evidenced findings on matching changed files.

- Use the bundle checker for `JSON_BOM`, `JSON_ENCODING`, `JSON_SYNTAX`,
  `JSON_DUPLICATE_KEY`, `JSON_NON_FINITE`, `JSON_UNSAFE_INTEGER`,
  `JSON_NUMBER_RANGE`, and `JSON_UNPAIRED_SURROGATE` findings.
- Review BOM/UTF-8 handling, duplicate keys, strict grammar, and numeric interoperability
  at the format boundary.
- Remember that object order is not semantic in JSON; report ordering only
  when a consuming owner explicitly defines presentation requirements.
- Separately review schema-sensitive key or type changes, required properties,
  identifiers or enums, and content meaning against an evidenced local contract.
- Report secret exposure and contradictory defaults when the changed file
  provides evidence; route broader domain semantics to the owning instruction.
