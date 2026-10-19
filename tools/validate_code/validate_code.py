#!/usr/bin/env python3
"""Run repository-owned static, Python, and Terraform validation units."""

from __future__ import annotations

import argparse
import hashlib
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from tools.validation_core import (
    EventSink,
    RepositorySnapshot,
    RunContext,
    RunReport,
    UnitResult,
    ValidationUnit,
    render_run,
    run_command,
    run_units,
    write_run_result,
    write_unit_log,
)
from tools.validation_core.events import LiveEventWriter

DEFAULT_TMP_DIR = Path("tmp/validate-code")
DEFAULT_MAX_PARALLEL = min(4, os.cpu_count() or 1)


@dataclass(frozen=True)
class StaticCheck:
    name: str
    build: Callable[[RunContext], int]


@dataclass(frozen=True)
class PythonShard:
    name: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class TerraformLane:
    name: str
    roots: tuple[str, ...]


def _relative_paths(root: Path, patterns: Iterable[str]) -> tuple[Path, ...]:
    paths: set[Path] = set()
    for pattern in patterns:
        base_pattern = pattern[:-3] if pattern.endswith("/**") else pattern
        if any(character in base_pattern for character in "*?["):
            matches = root.glob(base_pattern)
        else:
            matches = (root / base_pattern,)
        for match in matches:
            if match.exists():
                paths.add(match)
    return tuple(sorted(paths))


def _run_many(context: RunContext, commands: Sequence[Sequence[str | Path]]) -> int:
    status = 0
    for command in commands:
        current = run_command(context, command)
        if current:
            status = max(status, current, 1)
    return status


def _actionlint(context: RunContext) -> int:
    workflows = sorted(
        path
        for pattern in ("*.yml", "*.yaml")
        for path in (context.root / ".github/workflows").glob(pattern)
        if path.is_file()
    )
    actionlint = shutil.which("actionlint") or "actionlint"
    return run_command(context, [actionlint, *workflows])


EXCLUDED_PARTS = {".git", ".venv", "venv", ".terraform", "__pycache__", "node_modules"}
SOURCE_AREAS = (
    "scripts",
    "src",
    "tools",
    "tests",
    ".github/actions",
    ".github/tools",
    ".identity",
)


def _source_files(root: Path, suffix: str) -> tuple[Path, ...]:
    candidates = list(root.glob(f"*{suffix}"))
    for area in SOURCE_AREAS:
        candidates.extend((root / area).rglob(f"*{suffix}"))
    return tuple(
        sorted(
            {
                candidate
                for candidate in candidates
                if candidate.is_file()
                and not EXCLUDED_PARTS.intersection(candidate.relative_to(root).parts)
            }
        )
    )


def _shell(context: RunContext) -> int:
    targets = _source_files(context.root, ".sh")
    status = _run_many(context, [["bash", "-n", target] for target in targets])
    if targets:
        status = max(
            status, run_command(context, ["shellcheck", "--severity=warning", *targets])
        )
    return status


def _python_dependencies(context: RunContext) -> int:
    return run_command(context, [sys.executable, "-m", "pip", "check"])


def _python_compile(context: RunContext) -> int:
    targets = _source_files(context.root, ".py")
    return _run_many(
        context,
        [
            [
                sys.executable,
                "-X",
                f"pycache_prefix={context.tmp_dir / 'pycache'}",
                "-m",
                "py_compile",
                *targets,
            ]
        ]
        if targets
        else [],
    )


def _python_lint(context: RunContext) -> int:
    targets = _source_files(context.root, ".py")
    if not targets:
        return 0
    return _run_many(
        context,
        [
            ["ruff", "check", "--ignore", "E402", *targets],
            ["ruff", "format", "--check", *targets],
        ],
    )


STATIC_CHECKS = OrderedDict(
    (
        ("actionlint", StaticCheck("actionlint", _actionlint)),
        ("shell-static-analysis", StaticCheck("shell-static-analysis", _shell)),
        (
            "python-dependencies",
            StaticCheck("python-dependencies", _python_dependencies),
        ),
        (
            "python-static-analysis",
            StaticCheck("python-static-analysis", _python_compile),
        ),
        ("python-lint", StaticCheck("python-lint", _python_lint)),
    )
)

PYTHON_SHARDS = OrderedDict(
    (
        (
            "retirements-v2",
            PythonShard(
                "retirements-v2", ("tests/comitato/comitato_azure_retirements_v2",)
            ),
        ),
        (
            "governance-contracts",
            PythonShard("governance-contracts", ("tests/github", "tests/graphify")),
        ),
        (
            "validation-tools",
            PythonShard(
                "validation-tools",
                (
                    "tests/validate_code",
                    "tests/validation_core",
                    "tests/azure-policy/tools",
                ),
            ),
        ),
    )
)

TERRAFORM_LANES = OrderedDict(
    (
        ("azure-policy", TerraformLane("azure-policy", ("src/azure-policy",))),
        ("identity", TerraformLane("identity", (".identity",))),
    )
)


def _pytest_paths(root: Path, shard: PythonShard) -> tuple[Path, ...]:
    return _relative_paths(root, shard.paths)


def discover_pytest_node_ids(
    root: Path, paths: Sequence[Path] | None = None
) -> tuple[str, ...]:
    """Collect canonical top-level node IDs without executing tests."""

    selected = (
        list(paths)
        if paths is not None
        else [root / area for area in SOURCE_AREAS if (root / area).is_dir()]
    )
    if not selected:
        return ()
    command = [sys.executable, "-m", "pytest", "--collect-only", "-q", *selected]
    completed = subprocess.run(
        [str(value) for value in command],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )
    if completed.returncode not in (0, 5):
        raise ValueError(
            f"Pytest collection failed:\n{completed.stdout}\n{completed.stderr}"
        )
    node_ids = {
        line.strip()
        for line in completed.stdout.splitlines()
        if "::" in line and not line.startswith("=")
    }
    return tuple(sorted(node_ids))


def validate_python_shards(root: Path) -> dict[str, tuple[str, ...]]:
    """Return the path-owned collection and reject gaps or overlaps."""

    all_nodes = set(discover_pytest_node_ids(root))
    if not all_nodes:
        raise ValueError("Canonical Python collection is empty")
    ownership: dict[str, tuple[str, ...]] = {}
    seen: dict[str, str] = {}
    for name, shard in PYTHON_SHARDS.items():
        nodes = set(discover_pytest_node_ids(root, _pytest_paths(root, shard)))
        if not nodes:
            raise ValueError(f"Python shard {name} is empty")
        for node in nodes:
            if node in seen:
                raise ValueError(
                    f"Python node {node} belongs to {seen[node]} and {name}"
                )
            seen[node] = name
        ownership[name] = tuple(sorted(nodes))
    unmapped = all_nodes - set(seen)
    if unmapped:
        raise ValueError(f"Unmapped Python nodes: {', '.join(sorted(unmapped))}")
    if set(seen) != all_nodes:
        raise ValueError("Python shard union does not equal canonical collection")
    return ownership


def _discover_root_paths(base: Path) -> tuple[Path, ...]:
    roots: set[Path] = set()
    for source in base.rglob("*.tf"):
        if source.is_file() and not EXCLUDED_PARTS.intersection(
            source.relative_to(base).parts
        ):
            roots.add(source.parent)
    return tuple(sorted(roots, key=str))


def discover_terraform_roots(root: Path) -> tuple[str, ...]:
    return tuple(
        sorted(
            path.relative_to(root).as_posix()
            for area in ("src", ".identity")
            for path in _discover_root_paths(root / area)
        )
    )


def validate_terraform_lanes(root: Path) -> tuple[str, ...]:
    discovered = set(discover_terraform_roots(root))
    owners: dict[str, str] = {}
    for lane, manifest in TERRAFORM_LANES.items():
        for base in manifest.roots:
            for terraform_root in _discover_root_paths(root / base):
                relative = terraform_root.relative_to(root).as_posix()
                if relative in owners:
                    raise ValueError(f"Terraform root is duplicated: {relative}")
                owners[relative] = lane
    if discovered != set(owners):
        missing = sorted(set(owners) - discovered)
        unknown = sorted(discovered - set(owners))
        raise ValueError(
            f"Terraform manifest mismatch; missing={missing}, unknown={unknown}"
        )
    return tuple(sorted(discovered))


def _python_stamp(root: Path, tmp_dir: Path) -> Path:
    requirements = root / "src/comitato/comitato_azure_retirements_v2/requirements.txt"
    digest = hashlib.sha256()
    digest.update(sys.version.encode())
    if requirements.is_file():
        digest.update(requirements.read_bytes())
    stamp = tmp_dir / "python-environment.stamp"
    stamp.parent.mkdir(parents=True, exist_ok=True)
    if not stamp.is_file() or stamp.read_text(encoding="utf-8") != digest.hexdigest():
        stamp.write_text(digest.hexdigest(), encoding="utf-8")
    return stamp


def run_python_shard(context: RunContext, shard: PythonShard) -> int:
    paths = _pytest_paths(context.root, shard)
    if not paths:
        return 1
    _python_stamp(context.root, context.tmp_dir)
    return run_command(context, [sys.executable, "-m", "pytest", "-q", *paths])


def _run_python_integrity(context: RunContext) -> int:
    if context.dry_run:
        return 0
    validate_python_shards(context.root)
    return 0


def _python_integrity_unit() -> ValidationUnit:
    return ValidationUnit(
        "python:integrity",
        "Python shard integrity",
        _run_python_integrity,
        parallelizable=False,
    )


def run_terraform_roots(
    context: RunContext, roots: Sequence[Path], *, lane_name: str
) -> int:
    if not roots:
        return 1
    if context.dry_run:
        return _run_terraform_commands(
            context, roots, context.tmp_dir / f"terraform-{lane_name}"
        )
    context.tmp_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f"terraform-{lane_name}-", dir=context.tmp_dir
    ) as data_root:
        return _run_terraform_commands(context, roots, Path(data_root))


def _run_terraform_commands(
    context: RunContext, roots: Sequence[Path], data_root: Path
) -> int:
    status = 0
    terraform_bin = os.environ.get("TERRAFORM_BIN", "terraform")
    for index, terraform_root in enumerate(roots):
        data_dir = data_root / str(index)
        if not context.dry_run:
            data_dir.mkdir(parents=True, exist_ok=True)
        environment = {"TF_DATA_DIR": str(data_dir), "TF_IN_AUTOMATION": "1"}
        prefix = [terraform_bin, f"-chdir={terraform_root}"]
        current = run_command(
            context, [*prefix, "fmt", "-check", "-diff"], env=environment
        )
        status = max(status, current)
        current = run_command(
            context,
            [
                *prefix,
                "init",
                "-backend=false",
                "-input=false",
                "-lockfile=readonly",
                "-no-color",
            ],
            env=environment,
        )
        status = max(status, current)
        if current:
            continue
        status = max(
            status,
            run_command(context, [*prefix, "validate", "-no-color"], env=environment),
        )
        if any((terraform_root / "tests").glob("*.tftest.hcl")) or any(
            terraform_root.glob("*.tftest.hcl")
        ):
            status = max(
                status,
                run_command(context, [*prefix, "test", "-no-color"], env=environment),
            )
    return status


def run_terraform_lane(context: RunContext, lane: TerraformLane) -> int:
    roots = [
        terraform_root
        for relative in lane.roots
        for terraform_root in _discover_root_paths(context.root / relative)
    ]
    return run_terraform_roots(context, roots, lane_name=lane.name)


def _unit_catalog(root: Path, selected: Sequence[str]) -> list[ValidationUnit]:
    units: list[ValidationUnit] = []
    for name in selected:
        check = STATIC_CHECKS[name]
        units.append(ValidationUnit(f"static:{name}", check.name, check.build))
    for name in selected:
        if name in PYTHON_SHARDS:
            shard = PYTHON_SHARDS[name]
            units.append(
                ValidationUnit(
                    f"python:{name}",
                    f"Python shard {name}",
                    lambda context, current=shard: run_python_shard(context, current),
                )
            )
    return units


def _make_units(
    root: Path, stream: str | None, args: argparse.Namespace
) -> list[ValidationUnit]:
    units: list[ValidationUnit] = []
    if args.integrity_only:
        return [_python_integrity_unit()]
    if (
        not args.group
        and stream in (None, "python")
        and not args.leaf
        and not args.lane
        and not args.terraform_root
    ):
        units.append(_python_integrity_unit())
    if stream is None or stream == "static":
        names = [args.leaf] if args.leaf else list(STATIC_CHECKS)
        for name in names:
            check = STATIC_CHECKS[name]
            units.append(ValidationUnit(f"static:{name}", check.name, check.build))
    if stream is None or stream == "python":
        names = [args.group] if args.group else list(PYTHON_SHARDS)
        for name in names:
            shard = PYTHON_SHARDS[name]
            units.append(
                ValidationUnit(
                    f"python:{name}",
                    f"Python shard {name}",
                    lambda context, current=shard: run_python_shard(context, current),
                )
            )
    if stream is None or stream == "terraform":
        if args.terraform_root:
            root_path = Path(args.terraform_root)
            if not root_path.is_absolute():
                root_path = root / root_path
            roots = list(_discover_root_paths(root_path))
            if not roots and (root_path / "tests").is_dir():
                roots = [root_path]
            units.append(
                ValidationUnit(
                    "terraform:compatibility",
                    "Terraform compatibility root",
                    lambda context: run_terraform_roots(
                        context, roots, lane_name="compatibility"
                    ),
                )
            )
        else:
            names = [args.lane] if args.lane else list(TERRAFORM_LANES)
            for name in names:
                lane = TERRAFORM_LANES[name]
                families: dict[str, list[Path]] = {}
                for relative in lane.roots:
                    base = root / relative
                    for terraform_root in _discover_root_paths(base):
                        parts = terraform_root.relative_to(base).parts
                        family = parts[0] if parts else "root"
                        families.setdefault(family, []).append(terraform_root)
                for family, roots in sorted(families.items()):
                    units.append(
                        ValidationUnit(
                            f"terraform:{name}:{family}",
                            f"Terraform {name}/{family}",
                            lambda context, current=tuple(roots), label=family: (
                                run_terraform_roots(context, current, lane_name=label)
                            ),
                        )
                    )
    return units


def _print_catalog() -> None:
    print("STATIC")
    for name in STATIC_CHECKS:
        print(f"  {name}")
    print("PYTHON")
    for name, shard in PYTHON_SHARDS.items():
        print(f"  {name}: {', '.join(shard.paths)}")
    print("TERRAFORM")
    for name, lane in TERRAFORM_LANES.items():
        print(f"  {name}: {', '.join(lane.roots)}")


def _resolve_path(root: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return (root / path).resolve() if not path.is_absolute() else path.resolve()


def _capture_snapshot(root: Path) -> RepositorySnapshot | None:
    try:
        return RepositorySnapshot.capture(root)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def _unit_log_text(result: UnitResult) -> str:
    lines = [
        f"unit={result.unit.unit_id}",
        f"status={result.status or ('passed' if result.exit_code == 0 else 'failed')}",
        f"exit_code={result.exit_code}",
    ]
    for command in result.commands:
        lines.append(f"$ {command.command} [{command.exit_code}]")
        if command.stdout.strip():
            lines.append(f"stdout: {command.stdout}")
        if command.stderr.strip():
            lines.append(f"stderr: {command.stderr}")
    return "\n".join(lines)


def _prepare_report(
    results,
    context: RunContext,
    *,
    request: str,
    selectors: Sequence[str],
    before: RepositorySnapshot | None,
    artifact_dir: Path | None,
) -> RunReport:
    report = getattr(results, "report", None)
    if not isinstance(report, RunReport):
        report = RunReport(
            results=tuple(results),
            planned_units=tuple(result.unit.unit_id for result in results),
            serial_equivalent_seconds=sum(
                result.duration_seconds for result in results
            ),
            wall_clock_seconds=sum(result.duration_seconds for result in results),
            queue_seconds=sum(result.queue_seconds for result in results),
        )
    report = replace(
        report,
        request=request,
        selectors=tuple(selectors),
        context=context,
        artifact_root=artifact_dir,
        repository_before=before,
    )
    if artifact_dir is not None:
        updated_results: list[UnitResult] = []
        for result in report.results:
            reference = write_unit_log(
                result.unit.unit_id,
                _unit_log_text(result),
                artifact_dir,
            )
            updated_results.append(
                replace(result, artifacts=tuple(result.artifacts) + (str(reference),))
            )
        report = replace(report, results=tuple(updated_results))
    after = _capture_snapshot(context.root)
    delta = before.delta(after) if before is not None and after is not None else None
    return replace(
        report,
        repository_after=after,
        repository_delta=delta,
        artifacts=tuple(
            artifact for result in report.results for artifact in result.artifacts
        ),
    )


def _validation_exit(report: RunReport) -> int:
    return (
        1
        if any(
            result.exit_code != 0 or result.status in {"failed", "incomplete"}
            for result in report.results
        )
        else 0
    )


def _finish(report: RunReport, output_format: str, result_path: Path | None) -> int:
    validation_exit = _validation_exit(report)
    if result_path is not None:
        try:
            write_run_result(report, result_path)
        except Exception as error:
            print(f"validation result publication failure: {error}", file=sys.stderr)
    try:
        print(render_run(report, output_format))
    except Exception as error:
        print(f"validation renderer failure: {error}", file=sys.stderr)
    return validation_exit


class _SingleValueSelector(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[str] | None,
        option_string: str | None = None,
    ) -> None:
        if getattr(namespace, self.dest, None) is not None:
            raise argparse.ArgumentError(self, "may be specified only once")
        setattr(namespace, self.dest, values)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stream", nargs="?", choices=("static", "python", "terraform"))
    for selector in ("--leaf", "--group", "--vertical", "--lane", "--terraform-root"):
        parser.add_argument(selector, action=_SingleValueSelector)
    parser.add_argument("--serial", action="store_true")
    parser.add_argument("--max-parallel", type=int, default=DEFAULT_MAX_PARALLEL)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--tmp-dir", default=str(DEFAULT_TMP_DIR))
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument(
        "--format",
        choices=("auto", "terminal", "ci", "json", "markdown"),
        default="auto",
        dest="output_format",
    )
    parser.add_argument("--result-path")
    parser.add_argument("--artifact-dir")
    parser.add_argument("--integrity-only", action="store_true")
    parser.add_argument("--root", default=".")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    root = Path(args.root).resolve()
    if args.max_parallel < 1:
        print("ERROR: --max-parallel must be positive", file=sys.stderr)
        return 2
    if args.list:
        _print_catalog()
        return 0
    if args.vertical:
        if args.stream not in (None, "terraform"):
            print("ERROR: --vertical is only valid for terraform", file=sys.stderr)
            return 2
        args.lane = args.vertical
    if args.leaf and args.stream != "static":
        print("ERROR: --leaf is only valid for static", file=sys.stderr)
        return 2
    if args.group and args.stream != "python":
        print("ERROR: --group is only valid for python", file=sys.stderr)
        return 2
    if args.integrity_only:
        if args.stream != "python":
            print("ERROR: --integrity-only requires the python stream", file=sys.stderr)
            return 2
        if any((args.group, args.leaf, args.vertical, args.lane, args.terraform_root)):
            print(
                "ERROR: --integrity-only cannot be combined with another selector",
                file=sys.stderr,
            )
            return 2
    if args.lane and args.stream not in (None, "terraform"):
        print("ERROR: --lane is only valid for terraform", file=sys.stderr)
        return 2
    catalogs = {
        "leaf": STATIC_CHECKS,
        "group": PYTHON_SHARDS,
        "lane": TERRAFORM_LANES,
    }
    for option, value in (
        ("leaf", args.leaf),
        ("group", args.group),
        ("lane", args.lane),
    ):
        if value and value not in catalogs[option]:
            print(
                f"ERROR: unknown {option} {value!r}; valid values: {', '.join(catalogs[option])}",
                file=sys.stderr,
            )
            return 2
    if args.stream is None and any((args.leaf, args.group, args.vertical, args.lane)):
        print("ERROR: a selector requires its stream", file=sys.stderr)
        return 2
    tmp_dir = Path(args.tmp_dir)
    if not tmp_dir.is_absolute():
        tmp_dir = root / tmp_dir
    artifact_dir = _resolve_path(root, args.artifact_dir)
    result_path = _resolve_path(root, args.result_path)
    raw_arguments = list(argv) if argv is not None else sys.argv[1:]
    request = shlex.join(str(argument) for argument in raw_arguments)
    live_writer = LiveEventWriter(sys.stderr)
    sink = EventSink(writer=live_writer.write)
    sink.emit(
        phase="preflight",
        unit_id=None,
        status="planned",
        detail=f"request={request} stream={args.stream or 'all'}",
    )
    selectors = tuple(
        value
        for value in (
            args.stream or "all",
            args.leaf,
            args.group,
            args.vertical or args.lane,
        )
        if value
    )
    context = RunContext(
        root,
        tmp_dir,
        args.dry_run,
        args.no_color,
        event_sink=sink,
        invocation_id=sink.invocation_id,
        selectors=selectors,
        artifact_dir=artifact_dir,
        metadata={"request": request, "rerun_prefix": "scripts/validate-code.sh"},
        compact=args.compact,
    )
    before = _capture_snapshot(root)
    try:
        if args.stream in (None, "terraform"):
            if args.terraform_root:
                selected_root = (root / args.terraform_root).resolve()
                if not any(
                    selected_root.is_relative_to(root / area)
                    for area in ("src", ".identity")
                ):
                    raise ValueError(
                        "--terraform-root must be inside the repository src or .identity directory"
                    )
                if not _discover_root_paths(selected_root):
                    raise ValueError(
                        "--terraform-root contains no Terraform configurations"
                    )
            else:
                validate_terraform_lanes(root)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    units = _make_units(root, args.stream, args)
    max_parallel = 1 if args.serial else args.max_parallel
    results = run_units(
        units, context, fail_fast=args.fail_fast, max_parallel=max_parallel
    )
    report = _prepare_report(
        results,
        context,
        request=request,
        selectors=selectors,
        before=before,
        artifact_dir=artifact_dir,
    )
    return _finish(report, args.output_format, result_path)


if __name__ == "__main__":
    raise SystemExit(main())
