# Tests

This document defines repository test placement and discovery. Repository
behavioral tests must live under `tests/` in component-mirrored folders, so the
owner of a test is visible from its path. This includes Python tests that
exercise shell scripts through a subprocess boundary. Terraform native tests
must stay with the module they cover.

```text
tests/
  azure-policy/tools/            -> src/azure-policy/tools/prod-sec-remove-security-locks.sh
  comitato/comitato_azure_retirements_v2/
                                 -> src/comitato/comitato_azure_retirements_v2
  github/                        -> .github/ (Copilot inventory)
  graphify/                      -> scripts/graphify-watch.sh, Makefile, .gitattributes
  validate_code/                 -> tools/validate_code
  validation_core/               -> tools/validation_core
```

## Scope

- Python tests run under Pytest. The `validate-code.sh` shards map each folder
  to a group: `governance-contracts` (`github`, `graphify`),
  `validation-tools` (`validate_code`, `validation_core`,
  `azure-policy/tools`), and `retirements-v2` (`comitato`).
- A Python test outside a mapped folder fails the `python:integrity` check.
- Shell behavioral coverage runs through Pytest, including subprocess tests in
  `azure-policy/tools` and launcher tests in `validate_code`. The validation
  gate also runs `shellcheck` and `bash -n`; static checks do not replace
  behavioral tests. Tests that only inspect shell source do not prove runtime
  behavior.
- Terraform native tests stay with their module, for example
  `src/azure-policy/04_policy_assignments/tests/`.

## Run

Default Pytest discovery and VS Code discovery both select root `tests/`.
Use an environment with Pytest and the retirement runtime's hash-locked
requirements installed; collecting all tests imports those runtime dependencies.
The validation launcher uses `PYTHON_BIN` when set, then the retirement v2 venv
when present, then `python3`. Direct Pytest and editor runs must use a compatible
environment too. Missing dependencies fail collection; they must not be hidden
by narrowing default discovery.

```bash
python -m pytest
python -m pytest -q tests/validate_code tests/validation_core
python -m pytest -q tests/azure-policy/tools tests/graphify tests/github
python -m pytest -q tests/comitato/comitato_azure_retirements_v2
./validate-code.sh python --integrity-only
```

`make test-v2` intentionally remains scoped to
`tests/comitato/comitato_azure_retirements_v2` and uses that component's venv.
The Python integrity check verifies complete, disjoint shard ownership without
executing the collected tests.
