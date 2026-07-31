from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, TypeVar

from .domain.execution import RunContext, RunRequest, Scope
from .publication.model import PublicationCandidate, PublicationReceipt


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RuntimeEvent:
    level: str
    event: str
    message: str
    run_id: str
    context: Mapping[str, object] = field(default_factory=dict)


class RunObserver(Protocol):
    def emit(self, event: RuntimeEvent) -> None:
        ...


class NullRunObserver:
    def emit(self, event: RuntimeEvent) -> None:
        return None


class Validator(Protocol[T]):
    def validate(self, value: T, context: Any) -> Any:
        ...


class Clock(Protocol):
    def now(self) -> datetime:
        ...


class RunIdFactory(Protocol):
    def new_id(self) -> str:
        ...


class AdvisorSource(Protocol):
    def acquire(self, context: RunContext) -> Any:
        ...


class ServiceHealthSource(Protocol):
    def acquire(self, context: RunContext) -> Any:
        ...


class SubscriptionScopeSource(Protocol):
    def resolve(self, request: RunRequest, *, run_id: str = "") -> Scope:
        ...


class PlatformCatalogSource(Protocol):
    def load(self) -> Any:
        ...


class AtomicPublicationStore(Protocol):
    def publish(self, candidate: PublicationCandidate) -> PublicationReceipt:
        raise NotImplementedError
