from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class SourceRecord:
    subscription_id: str
    identity: str
    payload: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class SourcePage:
    subscription_id: str
    items: tuple[Mapping[str, Any], ...] = ()
    continuation_token: str | None = None


__all__ = ["SourcePage", "SourceRecord"]
