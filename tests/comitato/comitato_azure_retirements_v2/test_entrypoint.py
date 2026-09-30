import os
import shlex
import shutil
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3]
PROJECT = ROOT / "src/comitato/comitato_azure_retirements_v2"
SCRIPT = PROJECT / "comitato-azure-retirements-v2.py"


@dataclass
class LauncherResult:
    returncode: int
    stdout: str
    stderr: str
    recorded_arguments: str


@dataclass
class FakeV2Launcher:
    root: Path
    launcher: Path
    record: Path

    def _environment(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment["FAKE_RECORD"] = str(self.record)
        return environment

    def _result(self, returncode: int, stdout: str, stderr: str) -> LauncherResult:
        recorded_arguments = (
            self.record.read_text(encoding="utf-8") if self.record.exists() else ""
        )
        return LauncherResult(returncode, stdout, stderr, recorded_arguments)

    def run(self, *arguments: str) -> LauncherResult:
        completed = subprocess.run(
            ["bash", str(self.launcher), *arguments],
            cwd=self.root,
            env=self._environment(),
            capture_output=True,
            text=True,
            check=False,
        )
        return self._result(completed.returncode, completed.stdout, completed.stderr)

    def run_non_tty(self, *arguments: str) -> LauncherResult:
        return self.run(*arguments)

    def run_tty(self, *arguments: str) -> LauncherResult:
        stdout_path = self.root / "interactive-stdout.txt"
        command = " ".join(
            [
                "bash",
                shlex.quote(str(self.launcher)),
                *(shlex.quote(argument) for argument in arguments),
                ">",
                shlex.quote(str(stdout_path)),
            ]
        )
        completed = subprocess.run(
            ["script", "-q", "/dev/null", "bash", "-c", command],
            cwd=self.root,
            env=self._environment(),
            capture_output=True,
            text=True,
            check=False,
        )
        return self._result(
            completed.returncode,
            stdout_path.read_text(encoding="utf-8") if stdout_path.exists() else "",
            completed.stdout + completed.stderr,
        )


@pytest.fixture
def fake_v2_launcher(tmp_path: Path) -> FakeV2Launcher:
    package = tmp_path / "src" / "comitato" / "comitato_azure_retirements_v2"
    package.mkdir(parents=True)
    launcher = package / "run.sh"
    shutil.copy2(ROOT / "src/comitato/comitato_azure_retirements_v2/run.sh", launcher)
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)

    fake_python = package / ".venv" / "bin" / "python"
    fake_python.parent.mkdir(parents=True)
    fake_python.write_text(
        '#!/bin/sh\nprintf \'%s\\n\' "$@" > "$FAKE_RECORD"\n',
        encoding="utf-8",
    )
    fake_python.chmod(fake_python.stat().st_mode | stat.S_IXUSR)
    return FakeV2Launcher(tmp_path, launcher, tmp_path / "recorded-arguments.txt")


def test_bash_entrypoint_help_is_bootstrap_free() -> None:
    result = subprocess.run(
        [
            "bash",
            str(ROOT / "src/comitato/comitato_azure_retirements_v2/run.sh"),
            "--help",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--report" in result.stdout


def test_project_root_contains_only_entry_layout() -> None:
    assert SCRIPT.is_file()
    entries = {
        path.name
        for path in PROJECT.iterdir()
        if not path.name.startswith(".")
    }
    assert sorted(path.name for path in PROJECT.glob("*.py")) == [
        "comitato-azure-retirements-v2.py"
    ]
    assert {name for name in entries if (PROJECT / name).is_dir()} == {
        "data",
        "exports",
        "retirements",
    }


def test_script_help_does_not_import_runtime_dependencies() -> None:
    assert SCRIPT.is_file()
    code = (
        f"import runpy, sys; sys.argv = [{str(SCRIPT)!r}, '--help']\n"
        "try:\n    runpy.run_path(sys.argv[0], run_name='__main__')\n"
        "except SystemExit as exc:\n    assert exc.code in (0, None)\n"
        "print('LOADED=' + ','.join(m for m in ('yaml', 'requests', 'rich') if m in sys.modules))"
    )
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "LOADED="


def test_script_uses_canonical_module_path() -> None:
    assert SCRIPT.is_file()
    code = (
        f"import runpy, sys; sys.argv = [{str(SCRIPT)!r}, '--help']\n"
        "try:\n    runpy.run_path(sys.argv[0], run_name='__main__')\n"
        "except SystemExit:\n    pass\n"
        "print('CANON=' + str('src.comitato.comitato_azure_retirements_v2.retirements.config' in sys.modules))\n"
        "print('SHADOW=' + str(any(m == 'retirements' or m.startswith('retirements.') for m in sys.modules)))"
    )
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-2:] == [
        "CANON=True",
        "SHADOW=False",
    ]


def test_script_help_from_foreign_cwd(tmp_path: Path) -> None:
    assert SCRIPT.is_file()
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--replay-bundle" in result.stdout


def test_script_short_help_is_available() -> None:
    assert SCRIPT.is_file()
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "-h"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--replay-bundle" in result.stdout


def test_copied_layout_launcher_help_needs_no_venv(tmp_path: Path) -> None:
    assert SCRIPT.is_file()
    copied_project = tmp_path / "src/comitato/comitato_azure_retirements_v2"
    copied_project.mkdir(parents=True)
    shutil.copy2(PROJECT / "run.sh", copied_project / "run.sh")
    shutil.copy2(SCRIPT, copied_project / SCRIPT.name)
    shutil.copytree(
        PROJECT / "retirements",
        copied_project / "retirements",
        ignore=shutil.ignore_patterns("__pycache__", ".venv"),
    )
    launcher = copied_project / "run.sh"
    launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR)
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)

    result = subprocess.run(
        ["bash", str(launcher), "--help"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--replay-bundle" in result.stdout
    assert not (copied_project / ".venv").exists()
    assert "ModuleNotFoundError" not in result.stderr


def test_launcher_invokes_script_instead_of_module(
    fake_v2_launcher: FakeV2Launcher,
) -> None:
    result = fake_v2_launcher.run("--report", "advisor")
    arguments = result.recorded_arguments.splitlines()

    assert result.returncode == 0
    assert arguments[0] == str(
        fake_v2_launcher.launcher.parent / "comitato-azure-retirements-v2.py"
    )
    assert "-m" not in arguments


def test_launcher_adds_human_format_when_no_format_is_given(
    fake_v2_launcher: FakeV2Launcher,
) -> None:
    result = fake_v2_launcher.run("--report", "advisor", "--subscriptions", "sub-1")

    assert result.returncode == 0
    assert "--output-format\nhuman\n" in result.recorded_arguments


@pytest.mark.parametrize(
    "format_arguments",
    (("--output-format=json",), ("--output-format", "json")),
)
def test_launcher_preserves_explicit_output_format_forms(
    fake_v2_launcher: FakeV2Launcher,
    format_arguments: tuple[str, ...],
) -> None:
    result = fake_v2_launcher.run(*format_arguments, "--report", "advisor")

    assert result.returncode == 0
    for argument in format_arguments:
        assert f"{argument}\n" in result.recorded_arguments
    assert result.recorded_arguments.count("--output-format") == 1


def test_launcher_suppresses_bootstrap_lines_in_non_tty(
    fake_v2_launcher: FakeV2Launcher,
) -> None:
    result = fake_v2_launcher.run_non_tty("--report", "advisor")

    assert result.returncode == 0
    assert result.stderr == ""


def test_launcher_sends_interactive_status_lines_to_stderr(
    fake_v2_launcher: FakeV2Launcher,
) -> None:
    result = fake_v2_launcher.run_tty("--report", "advisor")

    assert result.returncode == 0
    assert result.stdout == ""
    assert "Azure Retirements v2" in result.stderr
