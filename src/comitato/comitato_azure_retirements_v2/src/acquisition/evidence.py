from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class SourceRecord:
    subscription_id: str
    identity: str
    payload: Mapping[str, Any]
    source: str = ""
    page_number: int = 0
    continuation_token: str | None = None


@dataclass(frozen=True, slots=True)
class ObservationAccounting:
    source: str
    subscription_id: str
    source_identity: str
    destination: str
    reason: str = ""
    raw_record_ref: str = ""


@dataclass(frozen=True, slots=True)
class SourcePage:
    subscription_id: str
    items: tuple[Mapping[str, Any], ...] = ()
    continuation_token: str | None = None


__all__ = ["ObservationAccounting", "SourcePage", "SourceRecord"]
