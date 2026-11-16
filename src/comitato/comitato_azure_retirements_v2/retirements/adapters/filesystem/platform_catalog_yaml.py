from __future__ import annotations

import re
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path
from uuid import UUID

import yaml

from ...domain.platforms import (
    PlatformAssignment,
    PlatformCatalogSnapshot,
    SubscriptionId,
)


class CatalogLoadError(ValueError):
    """The source-of-truth catalog is missing or violates schema version 1."""


def _timestamp(value: object) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value
    ):
        raise CatalogLoadError(
            "platform catalog lifecycle timestamp must be UTC ISO 8601"
        )
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CatalogLoadError(
            "platform catalog lifecycle timestamp is invalid"
        ) from exc
    if parsed.year == 1:
        raise CatalogLoadError("platform catalog lifecycle timestamp is a sentinel")
    return parsed


def _periods(
    value: object,
    *,
    platform_history: bool,
    created_at: datetime | None,
    deleted_at: datetime | None,
) -> list[tuple[datetime, datetime | None, str | None]]:
    if not isinstance(value, list):
        raise CatalogLoadError("platform catalog lifecycle periods must be a list")
    result: list[tuple[datetime, datetime | None, str | None]] = []
    keys = {"started_at", "ended_at", "source"}
    if platform_history:
        keys.add("platform")
    for period in value:
        if not isinstance(period, dict) or set(period) != keys:
            raise CatalogLoadError("platform catalog lifecycle period shape is invalid")
        start, end = _timestamp(period["started_at"]), _timestamp(period["ended_at"])
        if start is None or (end is not None and start >= end):
            raise CatalogLoadError(
                "platform catalog lifecycle period bounds are invalid"
            )
        previous_end = result[-1][1] if result else None
        if (
            (created_at is not None and start < created_at)
            or (deleted_at is not None and (end is None or end > deleted_at))
            or (result and (previous_end is None or start < previous_end))
        ):
            raise CatalogLoadError(
                "platform catalog lifecycle periods overlap or exceed lifespan"
            )
        if not isinstance(period["source"], str) or not period["source"].strip():
            raise CatalogLoadError(
                "platform catalog lifecycle period source is required"
            )
        platform = period.get("platform")
        if platform_history and (
            not isinstance(platform, str)
            or not platform.strip()
            or platform.casefold() == "all"
        ):
            raise CatalogLoadError("platform catalog lifecycle platform is invalid")
        result.append((start, end, platform))
    return result


def _validate_lifecycle(
    value: object, identifier: object, state: str, platform: str
) -> None:
    if value is None:
        if identifier is not None:
            raise CatalogLoadError(
                "platform catalog lifecycle is null for a real subscription"
            )
        return
    keys = {
        "purchased_on",
        "created_at",
        "disabled_at",
        "deleted_at",
        "date_sources",
        "history_complete",
        "incomplete_reason",
        "activity_periods",
        "platform_assignments",
    }
    if identifier is None or not isinstance(value, dict) or set(value) != keys:
        raise CatalogLoadError("platform catalog lifecycle shape is invalid")
    purchase = value["purchased_on"]
    if purchase is not None:
        if not isinstance(purchase, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", purchase
        ):
            raise CatalogLoadError(
                "platform catalog lifecycle purchase date must be ISO 8601"
            )
        try:
            purchased_on = date.fromisoformat(purchase)
        except ValueError as exc:
            raise CatalogLoadError(
                "platform catalog lifecycle purchase date is invalid"
            ) from exc
        if purchased_on.year == 1:
            raise CatalogLoadError(
                "platform catalog lifecycle purchase date is a sentinel"
            )
    dates = {
        key: _timestamp(value[key])
        for key in ("created_at", "disabled_at", "deleted_at")
    }
    created = dates["created_at"]
    disabled = dates["disabled_at"]
    deleted = dates["deleted_at"]
    known_dates = [date for date in (created, disabled, deleted) if date is not None]
    if known_dates != sorted(known_dates) or (
        deleted is not None and state != "deleted"
    ):
        raise CatalogLoadError(
            "platform catalog lifecycle dates conflict with lifespan or state"
        )
    sources = value["date_sources"]
    source_keys = {key for key, instant in dates.items() if instant is not None}
    if purchase is not None:
        source_keys.add("purchased_on")
    if (
        not isinstance(sources, dict)
        or set(sources) != source_keys
        or any(
            not isinstance(source, str) or not source.strip()
            for source in sources.values()
        )
    ):
        raise CatalogLoadError(
            "platform catalog lifecycle dates require matching sources"
        )
    complete = value["history_complete"]
    reason = value["incomplete_reason"]
    if type(complete) is not bool or (
        (complete and reason is not None)
        or (not complete and (not isinstance(reason, str) or not reason.strip()))
    ):
        raise CatalogLoadError(
            "platform catalog lifecycle completeness requires an explicit reason"
        )
    activity = _periods(
        value["activity_periods"],
        platform_history=False,
        created_at=created,
        deleted_at=deleted,
    )
    assignments = _periods(
        value["platform_assignments"],
        platform_history=True,
        created_at=created,
        deleted_at=deleted,
    )
    if (activity and activity[-1][1] is None and state != "active") or (
        assignments and assignments[-1][1] is None and assignments[-1][2] != platform
    ):
        raise CatalogLoadError(
            "platform catalog lifecycle ongoing interval conflicts with current mapping"
        )
    if complete:
        if (
            created is None
            or not activity
            or not assignments
            or activity[0][0] != created
        ):
            raise CatalogLoadError(
                "platform catalog lifecycle complete history requires lifespan and periods"
            )
        last_start, last_end, _ = activity[-1]
        if (
            (state == "active" and last_end is not None)
            or (state == "disabled" and (disabled is None or last_end != disabled))
            or (
                state == "deleted"
                and (deleted is None or last_end != (disabled or deleted))
            )
            or (state == "active" and disabled is not None and disabled > last_start)
            or assignments[-1][2] != platform
            or (state == "active" and assignments[-1][1] is not None)
        ):
            raise CatalogLoadError(
                "platform catalog lifecycle complete history conflicts with current mapping"
            )
        closed_ends = [end for _, end, _ in activity if end is not None]
        if state == "deleted" and disabled is None:
            closed_ends = closed_ends[:-1]
        if disabled != (closed_ends[-1] if closed_ends else None):
            raise CatalogLoadError(
                "platform catalog lifecycle latest disable date conflicts with periods"
            )


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
        required_keys = {"schema_version", "platforms"}
        allowed_keys = required_keys | {"tenant_id"}
        if (
            not isinstance(payload, dict)
            or not required_keys.issubset(payload)
            or not set(payload).issubset(allowed_keys)
            or type(payload["schema_version"]) is not int
            or payload["schema_version"] != 1
            or not isinstance(payload["platforms"], dict)
        ):
            raise CatalogLoadError("platform catalog shape is not schema version 1")
        if "tenant_id" in payload:
            tenant_id = payload["tenant_id"]
            if not isinstance(tenant_id, str):
                raise CatalogLoadError("platform catalog tenant id is not a UUID")
            try:
                UUID(tenant_id)
            except ValueError as exc:
                raise CatalogLoadError(
                    "platform catalog tenant id is not a UUID"
                ) from exc
        assignments: list[PlatformAssignment] = []
        names: set[str] = set()
        seen_ids: set[str] = set()
        for platform, definition in payload["platforms"].items():
            if (
                not isinstance(platform, str)
                or not platform.strip()
                or platform.casefold() == "all"
            ):
                raise CatalogLoadError("platform catalog has an invalid platform name")
            if (
                not isinstance(definition, dict)
                or set(definition) != {"subscriptions"}
                or not isinstance(definition["subscriptions"], list)
            ):
                raise CatalogLoadError("platform catalog platform shape is invalid")
            for item in definition["subscriptions"]:
                required_item_keys = {"name", "id", "state"}
                if (
                    not isinstance(item, dict)
                    or not required_item_keys.issubset(item)
                    or not set(item).issubset(required_item_keys | {"lifecycle"})
                ):
                    raise CatalogLoadError(
                        "platform catalog subscription shape is invalid"
                    )
                name, identifier, state = item["name"], item["id"], item["state"]
                if (
                    not isinstance(name, str)
                    or not name.strip()
                    or not isinstance(state, str)
                    or state not in {"active", "disabled", "deleted"}
                ):
                    raise CatalogLoadError(
                        "platform catalog subscription values are invalid"
                    )
                if "lifecycle" in item:
                    _validate_lifecycle(item["lifecycle"], identifier, state, platform)
                if identifier is None:
                    if state == "active":
                        raise CatalogLoadError(
                            "platform catalog active subscription id is null"
                        )
                    continue
                if not isinstance(identifier, str):
                    raise CatalogLoadError(
                        "platform catalog subscription id must be a string"
                    )
                try:
                    canonical = SubscriptionId(identifier)
                except (ValueError, AttributeError) as exc:
                    raise CatalogLoadError(
                        "platform catalog subscription id is not a UUID"
                    ) from exc
                if canonical.value in seen_ids:
                    raise CatalogLoadError(
                        "platform catalog contains duplicate subscription UUID"
                    )
                seen_ids.add(canonical.value)
                if state == "active":
                    folded_name = " ".join(name.split()).casefold()
                    if folded_name in names:
                        raise CatalogLoadError(
                            "platform catalog contains duplicate active names"
                        )
                    names.add(folded_name)
                    assignments.append(
                        PlatformAssignment(canonical, platform, name.strip())
                    )
        return PlatformCatalogSnapshot(
            1,
            sha256(raw).hexdigest(),
            tuple(sorted(assignments, key=lambda item: item.subscription_id.value)),
        )


__all__ = ["CatalogLoadError", "YamlPlatformCatalogSource"]
