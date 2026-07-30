from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID
from typing import Any

from .diagnostics import Diagnostic, ValidationResult


@dataclass(frozen=True, slots=True)
class SubscriptionId:
    value: str

    def __post_init__(self) -> None:
        canonical = str(UUID(self.value)).lower()
        object.__setattr__(self, "value", canonical)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PlatformAssignment:
    subscription_id: SubscriptionId
    platform: str
    subscription_name: str

    def __post_init__(self) -> None:
        if not self.platform.strip() or self.platform == "ALL":
            raise ValueError("platform name must be non-empty and not ALL")
        if not self.subscription_name.strip():
            raise ValueError("subscription name must be non-empty")


@dataclass(frozen=True, slots=True)
class PlatformCatalogSnapshot:
    schema_version: int
    sha256: str
    assignments: tuple[PlatformAssignment, ...]

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError("unsupported platform catalog schema")
        ids = [item.subscription_id.value for item in self.assignments]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate subscription assignment")

    def lookup(self, subscription_id: str) -> tuple[str, str] | None:
        canonical = SubscriptionId(subscription_id).value
        for assignment in self.assignments:
            if assignment.subscription_id.value == canonical:
                return assignment.platform, assignment.subscription_name
        return None

    @property
    def active_ids(self) -> tuple[str, ...]:
        return tuple(sorted(item.subscription_id.value for item in self.assignments))


@dataclass(frozen=True, slots=True)
class PlatformProjection:
    platforms: tuple[str, ...]
    platforms_subscriptions: dict[str, tuple[dict[str, str], ...]]


def project_platforms(
    subscription_ids: tuple[SubscriptionId, ...],
    is_explicit_global: bool,
    catalog: PlatformCatalogSnapshot,
    *,
    report: str = "aggregate",
    run_id: str = "",
    record_refs: dict[str, tuple[str, ...]] | None = None,
) -> ValidationResult[PlatformProjection]:
    unique = tuple(sorted({item.value for item in subscription_ids}))
    if is_explicit_global and unique:
        return ValidationResult.invalid((Diagnostic("error", "global_subscription_conflict", "mapping", report, run_id),))
    if is_explicit_global:
        return ValidationResult.valid(PlatformProjection(("ALL",), {"ALL": ()}))
    missing: list[Diagnostic] = []
    groups: dict[str, list[dict[str, str]]] = {}
    for raw_id in unique:
        assignment = catalog.lookup(raw_id)
        if assignment is None:
            refs = tuple(sorted(set((record_refs or {}).get(raw_id, ()))))
            missing.append(
                Diagnostic(
                    "error",
                    "platform_mapping_unmapped_subscription",
                    "mapping",
                    report,
                    run_id,
                    subscription_id=raw_id,
                    message=f"Publication blocked: subscription (name unavailable) ({raw_id}) has no active assignment in src/_source_of_truth/eng-finops-platforms.yaml",
                    context=(
                        ("subscription_name", ""),
                        ("record_refs", ",".join(refs)),
                    ),
                )
            )
            continue
        platform, name = assignment
        groups.setdefault(platform, []).append({"subscription_id": raw_id, "subscription_name": name})
    if missing:
        return ValidationResult.invalid(tuple(missing))
    ordered = {key: tuple(sorted(value, key=lambda item: item["subscription_id"])) for key, value in sorted(groups.items())}
    return ValidationResult.valid(PlatformProjection(tuple(ordered), ordered))


__all__ = ["PlatformAssignment", "PlatformCatalogSnapshot", "PlatformProjection", "SubscriptionId", "project_platforms"]
