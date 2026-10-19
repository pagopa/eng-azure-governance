import subprocess

import pytest

from tools.validate_code import validate_code as runner
from tools.validation_core import RunContext


@pytest.mark.parametrize(
    ("selector", "value"),
    [
        ("leaf", "python-lint"),
        ("group", "validation-tools"),
        ("vertical", "identity"),
        ("lane", "azure-policy"),
        ("terraform-root", "src/azure-policy"),
    ],
)
@pytest.mark.parametrize("equals_syntax", [False, True])
def test_single_selectors_preserve_requested_value(selector, value, equals_syntax):
    option = f"--{selector}"
    arguments = [f"{option}={value}"] if equals_syntax else [option, value]

    parsed = runner._parser().parse_args(arguments)

    assert getattr(parsed, selector.replace("-", "_")) == value


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


def write_gator_repository(root, version="3.23.1\n", suites=("required_pdb",)):
    if version is not None:
        (root / ".gator-version").write_text(version, encoding="utf-8")
    for name in suites:
        directory = (
            root / "src/azure-policy/02_policy_kubernetes/policy_rules/tests" / name
        )
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "suite.yaml").write_text(
            "apiVersion: test.gatekeeper.sh/v1alpha1\nkind: Suite\n",
            encoding="utf-8",
        )
    return root


def gator_context(root):
    return RunContext(root, root / "scratch", False, True)


def record_gator_commands(monkeypatch, status=0):
    commands = []

    def execute(context, arguments, **kwargs):
        commands.append((list(arguments), kwargs))
        return status

    monkeypatch.setattr(runner, "run_command", execute)
    return commands


def test_gatekeeper_leaf_is_registered_as_static_check():
    assert "gatekeeper-policy-tests" in runner.STATIC_CHECKS


def test_gatekeeper_leaf_fails_when_gator_is_missing(tmp_path, monkeypatch):
    write_gator_repository(tmp_path)
    monkeypatch.setattr(runner.shutil, "which", lambda name: None)
    commands = record_gator_commands(monkeypatch)
    assert runner._gatekeeper_policy_tests(gator_context(tmp_path)) != 0
    assert commands == []


def test_gatekeeper_leaf_fails_on_version_mismatch_before_verify(tmp_path, monkeypatch):
    write_gator_repository(tmp_path)
    monkeypatch.setattr(runner.shutil, "which", lambda name: "/fake/gator")
    monkeypatch.setattr(runner, "_gator_version", lambda gator: "3.22.0")
    commands = record_gator_commands(monkeypatch)
    assert runner._gatekeeper_policy_tests(gator_context(tmp_path)) != 0
    assert commands == []


@pytest.mark.parametrize("version", [None, "\n"])
def test_gatekeeper_leaf_fails_without_a_pinned_version(tmp_path, monkeypatch, version):
    write_gator_repository(tmp_path, version=version)
    monkeypatch.setattr(runner.shutil, "which", lambda name: "/fake/gator")
    monkeypatch.setattr(runner, "_gator_version", lambda gator: "3.23.1")
    commands = record_gator_commands(monkeypatch)
    assert runner._gatekeeper_policy_tests(gator_context(tmp_path)) != 0
    assert commands == []


def test_gatekeeper_leaf_fails_when_no_suite_is_found(tmp_path, monkeypatch):
    write_gator_repository(tmp_path, suites=())
    monkeypatch.setattr(runner.shutil, "which", lambda name: "/fake/gator")
    monkeypatch.setattr(runner, "_gator_version", lambda gator: "3.23.1")
    commands = record_gator_commands(monkeypatch)
    assert runner._gatekeeper_policy_tests(gator_context(tmp_path)) != 0
    assert commands == []


def test_gatekeeper_leaf_verifies_each_suite_in_stable_order(tmp_path, monkeypatch):
    write_gator_repository(tmp_path, suites=("statefulset_b", "deployment_a"))
    monkeypatch.setattr(runner.shutil, "which", lambda name: "/fake/gator")
    monkeypatch.setattr(runner, "_gator_version", lambda gator: "3.23.1")
    commands = record_gator_commands(monkeypatch)
    assert runner._gatekeeper_policy_tests(gator_context(tmp_path)) == 0
    assert [arguments for arguments, _ in commands] == [
        ["/fake/gator", "verify", "suite.yaml"],
        ["/fake/gator", "verify", "suite.yaml"],
    ]
    directories = [kwargs["cwd"].name for _, kwargs in commands]
    assert directories == ["deployment_a", "statefulset_b"]


def test_gatekeeper_leaf_fails_when_a_suite_fails(tmp_path, monkeypatch):
    write_gator_repository(tmp_path)
    monkeypatch.setattr(runner.shutil, "which", lambda name: "/fake/gator")
    monkeypatch.setattr(runner, "_gator_version", lambda gator: "3.23.1")
    record_gator_commands(monkeypatch, status=1)
    assert runner._gatekeeper_policy_tests(gator_context(tmp_path)) != 0
