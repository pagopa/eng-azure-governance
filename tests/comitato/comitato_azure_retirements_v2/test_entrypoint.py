from pathlib import Path
import subprocess


ROOT = Path(__file__).parents[3]


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
