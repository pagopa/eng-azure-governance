from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class ReportSelector(str, Enum):
    ALL = "all"
    ADVISOR = "advisor"
    SERVICE_HEALTH = "service-health"
    AGGREGATE = "aggregate"
    SLIDES = "slides"


@dataclass(frozen=True, slots=True)
class RunRequest:
    selector: ReportSelector
    subscription_ids: tuple[str, ...] = ()
    as_of_date: date | None = None


@dataclass(frozen=True, slots=True)
class Scope:
    subscription_ids: tuple[str, ...]
    mode: str = "resolved"

    def __post_init__(self) -> None:
        if tuple(sorted(set(self.subscription_ids))) != self.subscription_ids:
            raise ValueError("scope subscription_ids must be sorted and unique")


@dataclass(frozen=True, slots=True)
class CatalogIdentity:
    schema_version: int
    sha256: str

    def __post_init__(self) -> None:
        if self.schema_version < 1:
            raise ValueError("catalog schema_version must be positive")
        if len(self.sha256) != 64 or any(
            character not in "0123456789abcdef" for character in self.sha256
        ):
            raise ValueError("catalog sha256 must be lowercase hexadecimal")


@dataclass(frozen=True, slots=True)
class DependencyPlan:
    stages: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.stages or len(set(self.stages)) != len(self.stages):
            raise ValueError("dependency plan stages must be non-empty and unique")

    @property
    def needs_advisor(self) -> bool:
        return "advisor" in self.stages

    @property
    def needs_service_health(self) -> bool:
        return "service-health" in self.stages

    @property
    def needs_aggregate(self) -> bool:
        return "aggregate" in self.stages

    @property
    def needs_slides(self) -> bool:
        return "slides" in self.stages


@dataclass(frozen=True, slots=True)
class RunContext:
    run_id: str
    as_of_date: date
    created_at: datetime
    request: RunRequest
    scope: Scope
    catalog_identity: CatalogIdentity
    dependency_plan: DependencyPlan

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must be UTC-aware")
        if self.created_at.utcoffset().total_seconds() != 0:
            raise ValueError("created_at must be UTC-aware")
