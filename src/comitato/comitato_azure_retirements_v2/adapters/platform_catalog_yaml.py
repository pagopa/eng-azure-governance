from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any
from uuid import UUID

import yaml

from ..domain.platforms import PlatformAssignment, PlatformCatalogSnapshot, SubscriptionId


class CatalogLoadError(ValueError):
    """The source-of-truth catalog is missing or violates schema version 1."""


class YamlPlatformCatalogSource:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> PlatformCatalogSnapshot:
        try:
            raw = self.path.read_bytes()
        except OSError as exc:
            raise CatalogLoadError("platform catalog is unreadable") from exc
        try:
            payload = yaml.safe_load(raw.decode("utf-8"))
        except (UnicodeError, yaml.YAMLError) as exc:
            raise CatalogLoadError("platform catalog YAML is invalid") from exc
        if not isinstance(payload, dict) or set(payload) != {"schema_version", "platforms"} or payload["schema_version"] != 1 or not isinstance(payload["platforms"], dict):
            raise CatalogLoadError("platform catalog shape is not schema version 1")
        assignments: list[PlatformAssignment] = []
        names: set[str] = set()
        seen_ids: set[str] = set()
        for platform, definition in payload["platforms"].items():
            if not isinstance(platform, str) or not platform.strip() or platform == "ALL":
                raise CatalogLoadError("platform catalog has an invalid platform name")
            if not isinstance(definition, dict) or set(definition) != {"subscriptions"} or not isinstance(definition["subscriptions"], list):
                raise CatalogLoadError("platform catalog platform shape is invalid")
            for item in definition["subscriptions"]:
                if not isinstance(item, dict) or set(item) != {"name", "id", "state"}:
                    raise CatalogLoadError("platform catalog subscription shape is invalid")
                name, identifier, state = item["name"], item["id"], item["state"]
                if not isinstance(name, str) or not name.strip() or state not in {"active", "disabled", "deleted"}:
                    raise CatalogLoadError("platform catalog subscription values are invalid")
                if identifier is None:
                    raise CatalogLoadError("platform catalog subscription id is null")
                if not isinstance(identifier, str):
                    raise CatalogLoadError("platform catalog subscription id must be a string")
                try:
                    canonical = SubscriptionId(identifier)
                except (ValueError, AttributeError) as exc:
                    raise CatalogLoadError("platform catalog subscription id is not a UUID") from exc
                if canonical.value in seen_ids:
                    raise CatalogLoadError("platform catalog contains duplicate subscription UUID")
                seen_ids.add(canonical.value)
                if state == "active":
                    folded_name = " ".join(name.split()).casefold()
                    if folded_name in names:
                        raise CatalogLoadError("platform catalog contains duplicate active names")
                    names.add(folded_name)
                    assignments.append(PlatformAssignment(canonical, platform, name.strip()))
        return PlatformCatalogSnapshot(1, sha256(raw).hexdigest(), tuple(sorted(assignments, key=lambda item: item.subscription_id.value)))


__all__ = ["CatalogLoadError", "YamlPlatformCatalogSource"]
