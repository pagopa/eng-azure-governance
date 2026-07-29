"""Strict reader for the versioned Eng FinOps platform catalog."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from uuid import UUID

import yaml

from .workflow_exports_utils import normalize_key

SUPPORTED_SCHEMA_VERSION = 1
ALLOWED_STATES = frozenset({"active", "disabled", "deleted"})


def _catalog_error(catalog_path: Path, message: str) -> ValueError:
    return ValueError(f"Invalid Eng FinOps platform catalog {catalog_path}: {message}")


def load_active_subscription_platform_map(
    catalog_path: Path,
) -> dict[str, str]:
    """Return active normalized subscription names mapped to platform names."""
    try:
        payload = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise _catalog_error(catalog_path, f"invalid YAML: {exc}") from exc

    if not isinstance(payload, Mapping):
        raise _catalog_error(catalog_path, "root must be a mapping")
    if set(payload) != {"schema_version", "platforms"}:
        raise _catalog_error(
            catalog_path,
            "root must contain only schema_version and platforms",
        )

    schema_version = payload["schema_version"]
    if type(schema_version) is not int or schema_version != SUPPORTED_SCHEMA_VERSION:
        raise _catalog_error(
            catalog_path,
            f"unsupported schema_version {schema_version!r}; expected 1",
        )

    platforms = payload["platforms"]
    if not isinstance(platforms, Mapping):
        raise _catalog_error(catalog_path, "platforms must be a mapping")

    reverse_map: dict[str, str] = {}
    seen_ids: dict[UUID, str] = {}

    for platform_name, platform_payload in platforms.items():
        if not isinstance(platform_name, str) or not platform_name.strip():
            raise _catalog_error(catalog_path, "platform name must be non-empty")
        if (
            not isinstance(platform_payload, Mapping)
            or set(platform_payload) != {"subscriptions"}
        ):
            raise _catalog_error(
                catalog_path,
                f"platform {platform_name!r} must contain only subscriptions",
            )

        subscriptions = platform_payload["subscriptions"]
        if not isinstance(subscriptions, list):
            raise _catalog_error(
                catalog_path,
                f"platform {platform_name!r} subscriptions must be a list",
            )

        for index, subscription in enumerate(subscriptions):
            location = f"platforms.{platform_name}.subscriptions[{index}]"
            if (
                not isinstance(subscription, Mapping)
                or set(subscription) != {"name", "id", "state"}
            ):
                raise _catalog_error(
                    catalog_path,
                    f"{location} must contain only name, id, and state",
                )

            name = subscription["name"]
            state = subscription["state"]
            subscription_id = subscription["id"]
            if not isinstance(name, str) or not normalize_key(name):
                raise _catalog_error(catalog_path, f"{location}.name is invalid")
            if not isinstance(state, str) or state not in ALLOWED_STATES:
                raise _catalog_error(catalog_path, f"{location}.state is invalid")
            if subscription_id is None:
                if state == "active":
                    raise _catalog_error(
                        catalog_path,
                        f"{location} active subscription id cannot be null",
                    )
            elif not isinstance(subscription_id, str):
                raise _catalog_error(catalog_path, f"{location}.id must be a UUID")
            else:
                try:
                    parsed_id = UUID(subscription_id)
                except ValueError as exc:
                    raise _catalog_error(
                        catalog_path,
                        f"{location}.id must be a UUID",
                    ) from exc
                if parsed_id in seen_ids:
                    raise _catalog_error(
                        catalog_path,
                        f"{location} has duplicate subscription id also used by "
                        f"{seen_ids[parsed_id]}",
                    )
                seen_ids[parsed_id] = location

            if state != "active":
                continue
            normalized_name = normalize_key(name)
            if normalized_name in reverse_map:
                raise _catalog_error(
                    catalog_path,
                    f"{location} has duplicate active subscription name {name!r}",
                )
            reverse_map[normalized_name] = platform_name

    return reverse_map
