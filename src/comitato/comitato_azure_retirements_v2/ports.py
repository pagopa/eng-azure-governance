from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol, TypeVar

from .domain.execution import RunContext, RunRequest, Scope
from .publication.model import PublicationCandidate, PublicationReceipt


T = TypeVar("T")


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
    def resolve(self, request: RunRequest) -> Scope:
        ...


class PlatformCatalogSource(Protocol):
    def load(self) -> Any:
        ...


class AtomicPublicationStore(Protocol):
    def publish(self, candidate: PublicationCandidate) -> PublicationReceipt:
        raise NotImplementedError
