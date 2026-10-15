<!-- component-readme:v1 -->
# Validation Core

## Purpose

`tools/validation_core` provides infrastructure-only execution and reporting
mechanics for the code, business, and documentation validation CLIs. It is the
shared owner of the versioned lifecycle, evidence, timing, artifact, and report
contracts.

## Contents

- [Purpose](#purpose)
- [Responsibilities](#responsibilities)
- [Runtime contract](#runtime-contract)
- [Inputs and outputs](#inputs-and-outputs)
- [Dependencies](#dependencies)
- [Validation](#validation)

## Responsibilities

- Emit `validation-event/v1` lifecycle events through one serialized event
  sink and a shared stateful live writer. Event details are bounded and
  redacted before a renderer or writer receives them; command-level noise is
  suppressed from the live human view.
- Capture bounded, redacted subprocess evidence with head-plus-tail previews
  and signal failures.
- Schedule independent units under one bounded outer concurrency boundary,
  honoring declared dependencies, shared resources, and explicit fail-fast
  behavior.
- Preserve started failures and deterministic input-order results.
- Keep wall-clock, serial-equivalent, queue, category, and per-unit durations
  distinct.
- Write `validation-run/v1` result JSON and bounded unit logs atomically below
  the caller-selected artifact root.
- Keep domain catalogs, aliases, business rules, and Terraform lane ownership
  out of the shared package.

## Runtime contract

The event status vocabulary is `planned`, `queued`, `running`, `passed`,
`failed`, `skipped`, `cancelled`, and `incomplete`. A run starts with a
`preflight` event and a planned-unit projection before collection or command
execution. The final report retains every selected unit, including work that
was not started after an explicit fail-fast decision or a dependency failure.

Command arguments and output are redacted before they reach terminal, CI-line,
JSON, Markdown, or log-file output. Repository snapshots record branch,
commit, clean/dirty state, and a logical status digest; they do not copy file
contents or mutate Git. `validation-run/v1` keeps the repository delta and
structured next actions with the timings and unit states.

## Inputs and outputs

- Input: immutable `RunContext`, `ValidationUnit` callbacks, and selected
  concurrency or failure policies such as `max_parallel`, dependencies,
  resources, and `fail_fast`.
- Output: typed command evidence, `validation-event/v1` events, unit results,
  isolated temporary paths, bounded unit logs, and a deterministic
  `validation-run/v1` operator report. Renderers provide separate terminal,
  line-oriented CI, JSON, and Markdown projections. The terminal renderer
  supports dense default output, bounded Python/Terraform diagnostics, and
  terminal-only compact output; machine projections keep their existing shape.

Human projections do not invent expected values, actual values, root causes, or
rerun commands. They show bounded observed command output. A local rerun is
shown only when an explicit local launcher is available and the request is not
hosted-runner-specific; otherwise the projection says `No safe local rerun is
available`. The `validation-run/v1` JSON contract remains the machine-readable
source of truth.

## Dependencies

- Python standard library only.
- Native tests under `tools/validation_core/tests` and the repository Pytest
  surface.

## Validation

```bash
python3 -m pytest -q tools/validation_core/tests
python3 -m compileall -q tools/validation_core
```
