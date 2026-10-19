import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def invoke(*arguments, cwd=None):
    launcher = ROOT / "validate-code.sh"
    assert launcher.is_file(), "Azure code validation entrypoint is missing"
    return subprocess.run(
        [str(launcher), *arguments],
        cwd=cwd or ROOT,
        env=dict(os.environ, PYTHON_BIN=os.environ.get("PYTHON_BIN", "python3")),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_catalog_exposes_azure_groups_from_another_directory(tmp_path):
    result = invoke("--list", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "retirements-v2" in result.stdout
    assert "azure-policy" in result.stdout
    assert "identity" in result.stdout
    assert "governance-contracts" in result.stdout
    assert "platform-identity" not in result.stdout


def test_help_preserves_aws_execution_and_reporting_options():
    result = invoke("--help")
    assert result.returncode == 0, result.stderr
    for option in (
        "--serial",
        "--max-parallel",
        "--fail-fast",
        "--dry-run",
        "--list",
        "--compact",
        "--format",
        "--result-path",
        "--artifact-dir",
        "--integrity-only",
        "--terraform-root",
    ):
        assert option in result.stdout


def test_rejects_aws_lane_and_invalid_parallelism():
    for arguments in (
        ("terraform", "--lane", "platform-identity"),
        ("--max-parallel", "0"),
    ):
        result = invoke(*arguments)
        assert result.returncode == 2


@pytest.mark.parametrize(
    "selector", ["--leaf", "--group", "--vertical", "--lane", "--terraform-root"]
)
@pytest.mark.parametrize("second_value", ["first", "second"])
@pytest.mark.parametrize("syntax", ["separate", "equals", "mixed"])
def test_rejects_repeated_single_value_selectors_before_listing(
    selector, second_value, syntax, tmp_path
):
    if syntax == "separate":
        arguments = (selector, "first", selector, second_value)
    elif syntax == "equals":
        arguments = (f"{selector}=first", f"{selector}={second_value}")
    else:
        arguments = (selector, "first", f"{selector}={second_value}")
    scratch = tmp_path / "scratch"

    result = invoke("--list", "--tmp-dir", str(scratch), *arguments)

    assert result.returncode == 2, (result.stdout, result.stderr)
    assert selector in result.stderr
    assert "only once" in result.stderr
    assert result.stdout == ""
    assert not scratch.exists()


@pytest.mark.parametrize(
    "selector", ["--leaf", "--group", "--vertical", "--lane", "--terraform-root"]
)
def test_single_value_selectors_still_allow_listing(selector):
    result = invoke("--list", selector, "first")

    assert result.returncode == 0, result.stderr
    assert "azure-policy" in result.stdout


def test_azure_dry_run_reports_commands_without_running_them(tmp_path):
    result = invoke(
        "terraform",
        "--lane",
        "azure-policy",
        "--dry-run",
        "--format",
        "json",
        "--tmp-dir",
        str(tmp_path / "scratch"),
    )
    assert result.returncode == 0, result.stderr
    assert "azure-policy" in result.stdout
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "validation-run/v1"
    assert "apply" not in result.stdout
    assert "plan -" not in result.stdout
    assert not any((tmp_path / "scratch").rglob(".terraform.lock.hcl"))
