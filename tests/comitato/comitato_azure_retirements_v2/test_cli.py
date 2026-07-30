import json
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements_v2 import cli


def test_main_writes_one_success_result_to_stdout(monkeypatch, capsys) -> None:
    class Result:
        exit_status = 0

        def to_dict(self):
            return {"status": "published", "artifacts": ["one.tsv"]}

    monkeypatch.setattr(cli, "run_config", lambda config: Result())

    assert cli.main(["--output-path", "out"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out) == Result().to_dict()
    assert captured.err == ""


def test_main_writes_sorted_diagnostics_to_jsonl_stderr_and_returns_nonzero(monkeypatch, capsys) -> None:
    class Failure(Exception):
        diagnostics = (
            {"code": "z", "stage": "validation"},
            {"code": "a", "stage": "acquisition"},
        )

    def fail(config):
        raise Failure("safe failure")

    monkeypatch.setattr(cli, "run_config", fail)

    assert cli.main([]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert [json.loads(line)["code"] for line in captured.err.splitlines()] == ["a", "z"]


def test_python_module_help_is_available() -> None:
    assert callable(cli.main)
