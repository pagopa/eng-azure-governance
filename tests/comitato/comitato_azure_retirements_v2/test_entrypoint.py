import os
import pty
import shutil
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[3]


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
        recorded_arguments = self.record.read_text(encoding="utf-8") if self.record.exists() else ""
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
        master, slave = pty.openpty()
        process = subprocess.Popen(
            ["bash", str(self.launcher), *arguments],
            cwd=self.root,
            env=self._environment(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=slave,
        )
        os.close(slave)
        stdout, _ = process.communicate()
        stderr_chunks: list[bytes] = []
        try:
            while True:
                stderr_chunks.append(os.read(master, 4096))
        except OSError:
            pass
        finally:
            os.close(master)
        return self._result(
            process.returncode,
            stdout.decode("utf-8"),
            b"".join(stderr_chunks).decode("utf-8"),
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
        "#!/bin/sh\nprintf '%s\\n' \"$@\" > \"$FAKE_RECORD\"\n",
        encoding="utf-8",
    )
    fake_python.chmod(fake_python.stat().st_mode | stat.S_IXUSR)
    return FakeV2Launcher(tmp_path, launcher, tmp_path / "recorded-arguments.txt")


def test_bash_entrypoint_help_is_bootstrap_free() -> None:
    result = subprocess.run(
        ["bash", str(ROOT / "src/comitato/comitato_azure_retirements_v2/run.sh"), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--report" in result.stdout


def test_python_module_help_is_available_as_a_process() -> None:
    result = subprocess.run(
        ["python3", "-m", "src.comitato.comitato_azure_retirements_v2", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--report" in result.stdout


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
