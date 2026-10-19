# Tests

Root-level tests live here. Each folder mirrors the code it covers, so the
owner of a test is visible from its path.

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
- The repository has no Bash test files. Shell scripts are covered by
  `shellcheck` and `bash -n` in the validation gate.
- Terraform native tests stay with their module, for example
  `src/azure-policy/04_policy_assignments/tests/`.

## Run

```bash
python -m pytest -q tests/validate_code tests/validation_core
python -m pytest -q tests/azure-policy/tools tests/graphify tests/github
python -m pytest -q tests/comitato/comitato_azure_retirements_v2
```
