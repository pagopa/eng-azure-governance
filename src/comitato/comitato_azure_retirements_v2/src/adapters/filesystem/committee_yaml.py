"""Committee-owned slide values and their YAML/TSV persistence."""

from __future__ import annotations

import csv
import io
import json
import os
import shutil
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

_WRAPPED_FIELDS = frozenset({"comitato_descrizione", "descrizione_originale_completa"})
_WRAP_WIDTH = 100


class _CommitteeDumper(yaml.SafeDumper):
    pass


def _represent_mapping(dumper: yaml.SafeDumper, value: Mapping[str, Any]) -> yaml.Node:
    pairs = []
    for key in sorted(value):
        item = value[key]
        if key in _WRAPPED_FIELDS and isinstance(item, str) and len(item) > _WRAP_WIDTH:
            node = dumper.represent_scalar("tag:yaml.org,2002:str", item, style=">")
        else:
            node = dumper.represent_data(item)
        pairs.append((dumper.represent_data(key), node))
    return yaml.MappingNode("tag:yaml.org,2002:map", pairs)


_CommitteeDumper.add_representer(dict, _represent_mapping)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _tsv_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
    return str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")


def _tsv_bytes(value: Mapping[str, Any]) -> bytes:
    entries = [
        (item_id, entry if isinstance(entry, Mapping) else {})
        for item_id, entry in value.items()
    ]
    fields = sorted({field for _, entry in entries for field in entry})
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
    writer.writerow(("id_elemento", *fields))
    for item_id, entry in sorted(entries):
        writer.writerow(
            (str(item_id), *(_tsv_cell(entry.get(field, "")) for field in fields))
        )
    return stream.getvalue().encode("utf-8")


def write_tsv(path: Path, value: Mapping[str, Any]) -> None:
    tsv_path = path.with_suffix(".tsv")
    tsv_path.parent.mkdir(parents=True, exist_ok=True)
    tsv_path.write_bytes(_tsv_bytes(value))


def _stage_file(path: Path, data: bytes) -> None:
    with path.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        yaml_bytes = yaml.dump(
            dict(value), Dumper=_CommitteeDumper, allow_unicode=True, width=_WRAP_WIDTH
        ).encode("utf-8")
    except yaml.YAMLError as exc:
        raise OSError("committee YAML cannot be serialized") from exc
    staged_root = Path(tempfile.mkdtemp(prefix=f".{path.name}-", dir=path.parent))
    tsv_path = path.with_suffix(".tsv")
    pairs = (
        (staged_root / "committee.yaml", path, staged_root / "committee.yaml.previous"),
        (staged_root / "committee.tsv", tsv_path, staged_root / "committee.tsv.previous"),
    )
    state = [(False, False) for _ in pairs]
    try:
        _stage_file(pairs[0][0], yaml_bytes)
        _stage_file(pairs[1][0], _tsv_bytes(value))
        for index, (_, target, backup) in enumerate(pairs):
            if target.exists():
                os.replace(target, backup)
                state[index] = (True, False)
        for index, (staged, target, _) in enumerate(pairs):
            os.replace(staged, target)
            state[index] = (state[index][0], True)
    except OSError as exc:
        for index in reversed(range(len(pairs))):
            _, target, backup = pairs[index]
            previous_moved, new_moved = state[index]
            if new_moved:
                target.unlink(missing_ok=True)
            if previous_moved and backup.exists():
                os.replace(backup, target)
        raise OSError("committee YAML and TSV publication failed") from exc
    finally:
        shutil.rmtree(staged_root, ignore_errors=True)


__all__ = ["load", "write", "write_tsv"]
