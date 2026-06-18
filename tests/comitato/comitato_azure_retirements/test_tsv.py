from __future__ import annotations

from pathlib import Path

from src.comitato.comitato_azure_retirements.libs.tsv import compact_json, sanitize_cell, write_jsonl, write_tsv


def test_sanitize_cell_removes_tabs_and_newlines() -> None:
    assert sanitize_cell("a\tb\nc") == "a b c"


def test_compact_json_sorts_keys() -> None:
    assert compact_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'


def test_write_tsv_creates_header_and_rows(tmp_path: Path) -> None:
    output = tmp_path / "x.tsv"
    write_tsv(output, ["a", "b"], [{"a": "1", "b": "2"}])
    text = output.read_text(encoding="utf-8")
    assert text.splitlines()[0] == "a\tb"
    assert text.splitlines()[1] == "1\t2"


def test_write_jsonl_writes_one_item_per_line(tmp_path: Path) -> None:
    output = tmp_path / "items.jsonl"
    write_jsonl(output, [{"b": 2, "a": 1}, {"c": 3}])
    assert output.read_text(encoding="utf-8").splitlines() == ['{"a":1,"b":2}', '{"c":3}']
