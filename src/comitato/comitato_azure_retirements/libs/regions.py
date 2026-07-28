"""Allowed Azure regions for raw retirements exports."""

from __future__ import annotations

import re
from collections.abc import Collection
from pathlib import Path

REGIONS_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "azure_regions.conf"


def _region_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def load_allowed_regions(path: Path = REGIONS_CONFIG_PATH) -> frozenset[str]:
    regions: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.split("#", 1)[0].strip()
        if value:
            regions.add(_region_key(value))
    return frozenset(regions)


ALLOWED_REGIONS = load_allowed_regions()


def canonical_allowed_region(
    value: str, allowed_regions: Collection[str] = ALLOWED_REGIONS
) -> str:
    candidate = _region_key(value)
    if not candidate:
        return ""
    for region in allowed_regions:
        if _region_key(region) == candidate:
            return _region_key(region)
    return ""
