from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict, is_dataclass
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def encode_jsonl(records: Iterable[Any]) -> bytes:
    lines = [canonical_json(record) for record in records]
    return ("\n".join(lines) + ("\n" if lines else "")).encode("utf-8")


def decode_jsonl(data: bytes) -> tuple[Any, ...]:
    if not data:
        return ()
    return tuple(json.loads(line) for line in data.decode("utf-8").splitlines())


def _row_mapping(row: Any) -> Mapping[str, Any]:
    if isinstance(row, Mapping):
        return row
    if is_dataclass(row):
        return asdict(row)
    raise TypeError(f"contract row must be a mapping or dataclass, got {type(row)!r}")


def _cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple, bool)):
        value = canonical_json(value)
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _encode_cell(value: str, *, quote_empty: bool) -> str:
    if not value:
        return '""' if quote_empty else ""
    output = io.StringIO(newline="")
    csv.writer(output, delimiter="\t", lineterminator="\n").writerow((value,))
    return output.getvalue().removesuffix("\n")


def encode_tsv(header: tuple[str, ...], rows: Iterable[Any]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter="\t", lineterminator="\n")
    writer.writerow(header)
    for row in rows:
        mapping = _row_mapping(row)
        values = [_cell(mapping.get(column, "")) for column in header]
        last_value = max((index for index, value in enumerate(values) if value), default=-1)
        output.write(
            "\t".join(
                _encode_cell(value, quote_empty=index > last_value)
                for index, value in enumerate(values)
            )
            + "\n"
        )
    return output.getvalue().encode("utf-8")


def decode_tsv(data: bytes, expected_header: tuple[str, ...]) -> tuple[dict[str, str], ...]:
    reader = csv.reader(io.StringIO(data.decode("utf-8"), newline=""), delimiter="\t")
    rows = list(reader)
    if not rows or tuple(rows[0]) != expected_header:
        raise ValueError("TSV header does not match the versioned contract")
    if any(len(row) != len(expected_header) for row in rows[1:]):
        raise ValueError("TSV row does not match the versioned contract width")
    return tuple(dict(zip(expected_header, row, strict=True)) for row in rows[1:])
