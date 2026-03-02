---
description: Create or modify Python application components with DDD boundaries and tests
name: cs-python
agent: agent
argument-hint: action=<create|modify> component_type=<domain_service|entity|value_object|use_case|adapter|repository|module> component_name=<name> purpose=<purpose> [target_path=<path>]
---

# Python Project Task

## Context
Create or modify Python application components with DDD boundaries, early-return flow, and test coverage.

## Required inputs
- **Action**: ${input:action:create,modify}
- **Component type**: ${input:component_type:domain_service,entity,value_object,use_case,adapter,repository,module}
- **Component name**: ${input:component_name}
- **Purpose**: ${input:purpose}
- **Target path**: ${input:target_path:src}

## Instructions
1. Use the skill in `.github/skills/project-python/SKILL.md`.
2. Reuse repository naming and folder conventions.
3. Keep DDD boundaries explicit:
   - domain rules in domain-level modules
   - orchestration in use-case/application modules
   - I/O/SDK logic in adapters or repositories
4. Use early return and guard clauses.
5. Keep all code comments, logs, and exceptions in English.
6. If `action=modify`, preserve existing behavior unless explicit changes are requested.
7. If the task includes Python templates, use Jinja templates named `<file-name>.<extension>.j2`.
8. If `action=modify` and tests already exist, run existing tests before editing test files.
9. Add or update deterministic `pytest` unit tests only after the first test run, and only for intentional behavior changes or uncovered new behavior.

## Minimal example
- Input: `action=create component_type=domain_service component_name=PolicyEvaluator purpose="Evaluate policy eligibility"`
- Expected output:
  - New/updated Python component with DDD-aligned boundaries and guard clauses.
  - Deterministic pytest tests aligned with repository style.
  - No unintended behavioral drift outside requested changes.

## Validation
- Run lint/type checks when present.
- Run relevant `pytest` tests.
