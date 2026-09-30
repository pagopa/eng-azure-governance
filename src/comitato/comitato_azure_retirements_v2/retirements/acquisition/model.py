from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .evidence import ObservationAccounting


@dataclass(frozen=True, slots=True)
class AcquisitionReceipt:
    source: str
    api_version: str
    expected_subscriptions: int
    completed_subscriptions: int
    pages: int
    source_records: int
    complete: bool
    continuation_tokens: tuple[str, ...] = ()
    failed_subscriptions: tuple[str, ...] = ()
    completeness_reason: str = ""

    @property
    def is_complete(self) -> bool:
        return (
            self.complete
            and self.expected_subscriptions == self.completed_subscriptions
            and not self.failed_subscriptions
        )


@dataclass(frozen=True, slots=True)
class SourceAcquisition:
    receipt: AcquisitionReceipt
    records: tuple[Any, ...] = ()
    companion_records: tuple[Any, ...] = ()
    accounting: tuple[ObservationAccounting, ...] = ()
    collection_context: Mapping[str, Any] = field(default_factory=dict)
    response_context: tuple[Mapping[str, Any], ...] = ()
