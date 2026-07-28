"""Allowed Azure regions for raw retirements exports."""

from __future__ import annotations

import re
from collections.abc import Collection
from pathlib import Path

from .config import DEFAULT_REL_CONFIG, REL_CONFIG_PATH

REGIONS_CONFIG_PATH = REL_CONFIG_PATH


def _region_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def load_allowed_regions(path: Path = REGIONS_CONFIG_PATH) -> frozenset[str]:
    if path == REGIONS_CONFIG_PATH:
        return DEFAULT_REL_CONFIG.allowed_regions

    from .config import load_rel_config

    return load_rel_config(path).allowed_regions


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
