import subprocess

import pytest

from tools.validate_code import validate_code as runner
from tools.validation_core import RunContext


def write_configuration(root, relative):
    directory = root / relative
    directory.mkdir(parents=True)
    (directory / "main.tf").write_text("terraform {}\n", encoding="utf-8")
    return directory


def test_terraform_families_are_separate_parallel_units(tmp_path, monkeypatch):
    write_configuration(tmp_path, "src/azure-policy/02_policy_networking")
    write_configuration(tmp_path, "src/azure-policy/04_policy_assignments")
    write_configuration(tmp_path, "src/azure-policy/04_policy_assignments/modules/dev")
    args = runner._parser().parse_args(["terraform", "--lane", "azure-policy"])
    units = runner._make_units(tmp_path, "terraform", args)
    assert len(units) == 2, "Independent Azure policy families must run in parallel"
    captured = []

    def record_roots(context, roots, *, lane_name):
        captured.extend(roots)
        return 0

    monkeypatch.setattr(runner, "run_terraform_roots", record_roots)
    context = RunContext(tmp_path, tmp_path / "scratch", True, True)
    for unit in units:
        assert unit.parallelizable
        assert unit.run(context) == 0
    assert len(captured) == len(set(captured)) == 3


def test_failed_terraform_init_does_not_run_validate_or_test(tmp_path, monkeypatch):
    directory = write_configuration(tmp_path, "src/azure-policy/example")
    commands = []

    def execute(context, arguments, **kwargs):
        commands.append(arguments)
        assert kwargs["env"]["TF_DATA_DIR"].startswith(str(tmp_path / "scratch"))
        return 23 if "init" in arguments else 0

    monkeypatch.setattr(runner, "run_command", execute)
    context = RunContext(tmp_path, tmp_path / "scratch", False, True)
    assert runner.run_terraform_roots(context, [directory], lane_name="example") == 23
    assert [arguments[2] for arguments in commands] == ["fmt", "init"]
    assert "-backend=false" in commands[-1]
    assert "-lockfile=readonly" in commands[-1]


def test_native_test_is_run_only_for_a_root_with_test_files(tmp_path, monkeypatch):
    directory = write_configuration(tmp_path, "src/azure-policy/example")
    commands = []
    monkeypatch.setattr(
        runner,
        "run_command",
        lambda context, arguments, **kwargs: commands.append(arguments) or 0,
    )
    context = RunContext(tmp_path, tmp_path / "scratch", True, True)
    assert runner.run_terraform_roots(context, [directory], lane_name="example") == 0
    assert [arguments[2] for arguments in commands] == ["fmt", "init", "validate"]
    (directory / "tests").mkdir()
    (directory / "tests/example.tftest.hcl").write_text(
        'run "example" { command = plan }\n'
    )
    commands.clear()
    assert runner.run_terraform_roots(context, [directory], lane_name="example") == 0
    assert [arguments[2] for arguments in commands] == [
        "fmt",
        "init",
        "validate",
        "test",
    ]
    assert not (tmp_path / "scratch").exists()


def test_source_discovery_excludes_generated_and_virtualenv_files(tmp_path):
    for relative in (
        "src/service/main.py",
        "src/service/.venv/bad.py",
        "src/service/.terraform/bad.py",
        "validate.py",
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("", encoding="utf-8")
    assert runner._source_files(tmp_path, ".py") == (
        tmp_path / "src/service/main.py",
        tmp_path / "validate.py",
    )


def test_static_compilation_keeps_bytecode_outside_source_layout(tmp_path):
    target = tmp_path / "src/service/main.py"
    target.parent.mkdir(parents=True)
    target.write_text("value = 1\n", encoding="utf-8")
    context = RunContext(tmp_path, tmp_path / "scratch", False, True)
    assert runner._python_compile(context) == 0
    assert not (target.parent / "__pycache__").exists()
    assert tuple((context.tmp_dir / "pycache").rglob("*.pyc"))


def test_pytest_collection_failure_cannot_look_like_complete_shards(
    tmp_path, monkeypatch
):
    (tmp_path / "tests").mkdir()
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args, 2, "partial::node\n", "collection error"
        ),
    )
    with pytest.raises(ValueError, match="Pytest collection failed"):
        runner.discover_pytest_node_ids(tmp_path)


def test_terraform_catalog_rejects_unmapped_roots_and_external_paths(tmp_path):
    write_configuration(tmp_path, "src/unknown")
    with pytest.raises(ValueError, match="manifest mismatch"):
        runner.validate_terraform_lanes(tmp_path)
    assert (
        runner.main(
            ["--root", str(tmp_path), "terraform", "--terraform-root", "/", "--dry-run"]
        )
        == 1
    )


def test_python_shards_reject_gaps_and_duplicate_nodes(tmp_path, monkeypatch):
    for shard in runner.PYTHON_SHARDS.values():
        for relative in shard.paths:
            if "*" not in relative:
                (tmp_path / relative).mkdir(parents=True, exist_ok=True)
    collections = iter(
        [("first", "second", "third", "missing"), ("first",), ("second",), ("third",)]
    )
    monkeypatch.setattr(
        runner, "discover_pytest_node_ids", lambda *args: next(collections)
    )
    with pytest.raises(ValueError, match="Unmapped Python nodes"):
        runner.validate_python_shards(tmp_path)
    collections = iter([("first", "second"), ("first",), ("first",)])
    with pytest.raises(ValueError, match="belongs to"):
        runner.validate_python_shards(tmp_path)
