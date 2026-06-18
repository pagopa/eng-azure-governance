from __future__ import annotations

from pathlib import Path

from src.comitato.comitato_azure_retirements.libs.tsv import ensure_row, sanitize_cell, write_tsv


def test_sanitize_cell_removes_tabs_and_newlines() -> None:
    assert sanitize_cell("a\tb\nc") == "a b c"


def test_ensure_row_applies_schema_defaults() -> None:
    row = ensure_row({"a": "1"}, ["a", "b"])
    assert row == {"a": "1", "b": ""}


def test_write_tsv_creates_header_and_rows(tmp_path: Path) -> None:
    output = tmp_path / "x.tsv"
    write_tsv(output, [{"a": "1", "b": "2"}], ["a", "b"])
    text = output.read_text(encoding="utf-8")
    assert text.splitlines()[0] == "a\tb"
    assert text.splitlines()[1] == "1\t2"
