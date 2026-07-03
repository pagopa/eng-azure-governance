from __future__ import annotations

from pathlib import Path

from src.comitato.comitato_azure_retirements.libs.tsv import (
    compact_json,
    read_tsv,
    sanitize_cell,
    unique_tsv_rows,
    write_jsonl,
    write_tsv,
)


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


def test_unique_tsv_rows_deduplicates_after_sanitization() -> None:
    rows = unique_tsv_rows(
        ["a", "b"],
        [
            {"a": "1", "b": "line\nvalue"},
            {"a": "1", "b": "line value"},
            {"a": "2", "b": "value"},
        ],
    )

    assert rows == [{"a": "1", "b": "line value"}, {"a": "2", "b": "value"}]


def test_write_tsv_skips_duplicate_rows(tmp_path: Path) -> None:
    output = tmp_path / "x.tsv"
    write_tsv(output, ["a", "b"], [{"a": "1", "b": "2"}, {"a": "1", "b": "2"}])

    assert output.read_text(encoding="utf-8").splitlines() == ["a\tb", "1\t2"]


def test_write_jsonl_writes_one_item_per_line(tmp_path: Path) -> None:
    output = tmp_path / "items.jsonl"
    write_jsonl(output, [{"b": 2, "a": 1}, {"c": 3}])
    assert output.read_text(encoding="utf-8").splitlines() == [
        '{"a":1,"b":2}',
        '{"c":3}',
    ]


def test_read_tsv_returns_rows_by_header(tmp_path: Path) -> None:
    output = tmp_path / "rows.tsv"
    output.write_text("a\tb\n1\t2\n", encoding="utf-8")

    assert read_tsv(output) == [{"a": "1", "b": "2"}]
