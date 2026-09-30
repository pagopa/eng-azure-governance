"""Committee-owned slide values and their minimal YAML round-trip."""

from __future__ import annotations

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


def write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(
            dict(value), Dumper=_CommitteeDumper, allow_unicode=True, width=_WRAP_WIDTH
        ),
        encoding="utf-8",
    )


__all__ = ["load", "write"]
