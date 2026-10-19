# Code Validation

## Purpose

Run Azure Governance code checks through the execution and reporting structure
ported from `eng-aws-authorization-v2`. The repository owns its copy of the
runner; no sibling repository is required at runtime.

## Structure

- [../../validate-code.sh](../../validate-code.sh) delegates to the canonical
  [../../scripts/validate-code.sh](../../scripts/validate-code.sh) launcher.
- [validate_code.py](validate_code.py) owns Azure checks, selectors, Python shard
  integrity, and Terraform discovery.
- [../validation_core](../validation_core) owns bounded parallel execution,
  lifecycle events, redaction, timings, fail-fast, and reports. Its Python
  sources and tests were imported without changes from AWS v2.
- [../../tests/validate_code](../../tests/validate_code) owns adapter and
  direct-launcher regression tests. [../../tests/README.md](../../tests/README.md)
  defines repository test placement and discovery.

## Prerequisites

Use the repository Python version from `.python-version` and an environment with
Pytest and the retirement runtime's hash-locked requirements installed. The
launcher uses `PYTHON_BIN` when set, otherwise the existing retirement v2 venv,
otherwise `python3`. It works from outside the repository. It does not install
dependencies or create an environment automatically.

Terraform, actionlint, ShellCheck, and Ruff must be available for their selected
checks. Missing tools fail their units; they are not silently skipped.
`TERRAFORM_BIN` may select an alternative Terraform executable.

## Checks

Static leaves are `actionlint`, `shell-static-analysis`, `python-dependencies`,
`python-static-analysis`, and `python-lint`. They use Azure's workflow syntax,
Bash syntax and ShellCheck warning checks, selected-environment `pip check`,
Python compilation, and the non-mutating Ruff checks corresponding to the
repository pre-commit rules. Discovery excludes virtual environments, generated
Terraform directories, dependency trees, and skill bundles.

Python groups are `retirements-v2`, `governance-contracts`, and
`validation-tools`. All-stream and unscoped Python runs first verify that the
canonical Pytest collection is complete and disjoint across these groups.
Explicit group runs do not repeat that collection. Collection errors and empty
groups fail rather than looking like successful validation.

Terraform lanes are `azure-policy` and `identity`. Each policy family is an
independent parallel unit; assignment roots and their local modules run serially
within the same family. Discovery includes every `.tf` root under `src` and
`.identity`, and rejects roots outside the lane catalog.

Each root runs `fmt -check -diff`, `init -backend=false -input=false
-lockfile=readonly`, and `validate`. `terraform test` runs only when native test
files exist.
Initialization may download providers or modules, but it uses isolated
`TF_DATA_DIR` directories under `tmp/` and does not update lockfiles. The runner
never invokes plan, apply, or the operational `terraform.sh` wrappers. Future
native tests must own their provider mocking and resource-safety contract.

AWS-specific domain paths, synthetic test policy, inventory, migration ledger,
and documentation validators are not imported as Azure rules.

## Usage

From the repository root:

```bash
./validate-code.sh
./validate-code.sh --list
./validate-code.sh --dry-run --compact
./validate-code.sh --max-parallel 4 --fail-fast
./validate-code.sh --serial
./validate-code.sh static --leaf actionlint
./validate-code.sh python --group retirements-v2
./validate-code.sh python --integrity-only
./validate-code.sh terraform --lane azure-policy
./validate-code.sh terraform --vertical identity
./validate-code.sh terraform --terraform-root src/azure-policy/02_policy_networking
```

`--terraform-root` must select a repository path under `src` or `.identity`.
It runs that root and its nested configuration roots serially.

`--leaf`, `--group`, `--vertical`, `--lane`, and `--terraform-root` each accept
one occurrence per invocation. Repeating one returns exit code 2 before checks
or reports, even with equal values or `--option=value` syntax. A repetition does
not select multiple units. Run separate invocations to select different values.

`make lint` invokes the same unscoped `./validate-code.sh` gate and does not
invoke `make format`. Formatting is a separate, explicit operation.

## Reports And Timing

```bash
./validate-code.sh --format json \
  --result-path tmp/validate-code/result.json \
  --artifact-dir tmp/validate-code/artifacts
```

Options retain the AWS v2 interface: `--serial`, `--max-parallel`, `--fail-fast`,
`--dry-run`, `--list`, `--tmp-dir`, `--no-color`, `--compact`,
`--format auto|terminal|ci|json|markdown`, `--result-path`, and `--artifact-dir`.
Machine output stays on stdout; lifecycle updates use stderr. JSON uses the
`validation-run/v1` contract and records wall-clock time, serial-equivalent time,
queue time, command evidence, and every selected unit, including unstarted units
after fail-fast. Any failed or incomplete unit returns a nonzero status.

The `code-analysis` GitHub Actions job publishes a final workflow summary even
when a validation category fails. It shows category results, failed steps,
individual job durations, and direct links to job logs. If the job-details API
is unavailable, the summary falls back to category results. The required gate
still requires every category to succeed.

Each matrix job uploads `validation-*` artifacts containing `result.json` and
per-unit logs for seven days. No artifact is expected when setup fails before
validation starts. Failed command diagnostics also appear in the CI log,
separately from abbreviated lifecycle events. Job durations include setup and
must not be added together to estimate parallel workflow duration.

Dry-run records simulated commands without running validation subprocesses.
It may create temporary unit directories and explicitly requested reports.
Compare actual timings for equivalent selections and environments before
claiming a speedup; bounded parallelism alone is not a measured benchmark.

## Validation

```bash
python3 -m pytest -q tests/validate_code tests/validation_core
bash -n validate-code.sh scripts/validate-code.sh
shellcheck validate-code.sh scripts/validate-code.sh
ruff check tools/validate_code tools/validation_core
ruff format --check tools/validate_code tools/validation_core
./validate-code.sh --dry-run --format json
./validate-code.sh python --integrity-only
```
