from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID
from collections.abc import Mapping

from .diagnostics import Diagnostic, ValidationResult


@dataclass(frozen=True, slots=True)
class SubscriptionId:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("subscription ID must be a string")
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
        if not isinstance(self.platform, str) or not self.platform.strip() or self.platform.casefold() == "all":
            raise ValueError("platform name must be non-empty and not ALL")
        if not isinstance(self.subscription_name, str) or not self.subscription_name.strip():
            raise ValueError("subscription name must be non-empty")
        object.__setattr__(self, "platform", self.platform.strip())
        object.__setattr__(self, "subscription_name", self.subscription_name.strip())


@dataclass(frozen=True, slots=True)
class PlatformCatalogSnapshot:
    schema_version: int
    sha256: str
    assignments: tuple[PlatformAssignment, ...]

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("unsupported platform catalog schema")
        if (
            not isinstance(self.sha256, str)
            or len(self.sha256) != 64
            or any(character not in "0123456789abcdef" for character in self.sha256)
        ):
            raise ValueError("platform catalog sha256 must be lowercase hexadecimal")
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

    @property
    def subscription_ids(self) -> tuple[str, ...]:
        """Compatibility view used by the orchestration port."""
        return self.active_ids

    @property
    def identity(self):
        from .execution import CatalogIdentity

        return CatalogIdentity(self.schema_version, self.sha256)


@dataclass(frozen=True, slots=True)
class PlatformProjection:
    platforms: tuple[str, ...]
    platforms_subscriptions: dict[str, tuple[dict[str, str], ...]]

    def __post_init__(self) -> None:
        if tuple(sorted(set(self.platforms))) != self.platforms:
            raise ValueError("platform projection names must be sorted and unique")
        if tuple(self.platforms) != tuple(self.platforms_subscriptions):
            raise ValueError("platform projection keys must match platform names")
        if self.platforms == ("ALL",) and self.platforms_subscriptions != {"ALL": ()}:
            raise ValueError("global platform projection must be exactly ALL")

    @property
    def subscriptions(self) -> dict[str, tuple[dict[str, str], ...]]:
        return self.platforms_subscriptions


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
    ordered = {
        key: tuple(sorted(value, key=lambda item: item["subscription_id"]))
        for key, value in sorted(groups.items())
    }
    return ValidationResult.valid(PlatformProjection(tuple(ordered), ordered))


__all__ = ["PlatformAssignment", "PlatformCatalogSnapshot", "PlatformProjection", "SubscriptionId", "project_platforms"]
