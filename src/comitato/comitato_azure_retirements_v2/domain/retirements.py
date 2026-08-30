"""Canonical source-event identities and aggregate membership primitives."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True, slots=True, order=True)
class SourceEventKey:
    """Stable, case-insensitive key for one source event."""

    source: str
    identity: str

    def __post_init__(self) -> None:
        source = _text(self.source).casefold()
        identity = _text(self.identity).casefold()
        if not source or not identity:
            raise ValueError("source-event keys require a source and identity")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "identity", identity)

    @property
    def value(self) -> str:
        return f"{self.source}:{self.identity}"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SourceEvent:
    """All normalized rows that share one authoritative source identity."""

    key: SourceEventKey | tuple[str, str]
    source: str
    record_ref: str = ""
    row: Mapping[str, Any] = field(default_factory=dict)
    records: tuple[Mapping[str, Any], ...] = ()

    def __post_init__(self) -> None:
        key = self.key if isinstance(self.key, SourceEventKey) else SourceEventKey(*self.key)
        source = _text(self.source).casefold()
        if source != key.source:
            raise ValueError("source-event source does not match its key")
        rows = self.records or ((self.row,) if self.row else ())
        rows = tuple(rows)
        if rows and not self.row:
            object.__setattr__(self, "row", rows[0])
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "record_ref", _text(self.record_ref) or _text(rows[0].get("raw_record_ref")) if rows else _text(self.record_ref))
        object.__setattr__(self, "records", rows)


@dataclass(frozen=True, slots=True)
class AggregateId:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.startswith("azure-retirement:v1:"):
            raise ValueError("invalid aggregate ID")
        digest = self.value.removeprefix("azure-retirement:v1:")
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError("aggregate ID digest must be lowercase SHA-256")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class AggregateMembership:
    source_event_key: SourceEventKey | tuple[str, str]
    raw_record_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        key = self.source_event_key if isinstance(self.source_event_key, SourceEventKey) else SourceEventKey(*self.source_event_key)
        refs = tuple(sorted({_text(ref) for ref in self.raw_record_refs if _text(ref)}))
        if not refs:
            raise ValueError("aggregate membership requires a raw record reference")
        object.__setattr__(self, "source_event_key", key)
        object.__setattr__(self, "raw_record_refs", refs)

    @property
    def key(self) -> SourceEventKey:
        return self.source_event_key  # type: ignore[return-value]


def aggregate_id_for(keys: tuple[SourceEventKey, ...]) -> AggregateId:
    """Hash sorted complete keys using an unambiguous length-delimited encoding."""

    normalized = tuple(sorted({key if isinstance(key, SourceEventKey) else SourceEventKey(*key) for key in keys}))
    if not normalized:
        raise ValueError("aggregate identity requires at least one source-event key")
    encoded = bytearray()
    for key in normalized:
        value = key.value.encode("utf-8")
        encoded.extend(len(value).to_bytes(8, "big"))
        encoded.extend(value)
    return AggregateId(f"azure-retirement:v1:{sha256(bytes(encoded)).hexdigest()}")


def _rows(value: object) -> tuple[Mapping[str, Any], ...]:
    artifact = getattr(value, "artifact", None)
    if artifact is not None:
        return _rows(artifact)
    records = getattr(value, "records", None)
    if records is not None:
        return _rows(records)
    if isinstance(value, Mapping):
        return (value,)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return tuple(row for item in value for row in _rows(item))
    return ()


def _identity(source: str, row: Mapping[str, Any]) -> SourceEventKey:
    if source == "advisor":
        identity = _text(row.get("recommendation_type_id") or row.get("advisor_recommendation_type_id"))
        if not identity:
            identity = _text(row.get("advisor_recommendation_id"))
    else:
        identity = _text(row.get("tracking_id") or row.get("service_health_tracking_id"))
        if not identity:
            identity = _text(row.get("service_health_event_id"))
    return SourceEventKey(source, identity)


def build_source_events(
    advisor_records: object = (),
    service_health_records: object = (),
) -> tuple[tuple[SourceEvent, ...], tuple[AggregateMembership, ...]]:
    """Build deterministic source events and one membership per source key.

    The raw contracts reject duplicate references within a source. The final
    guard here also prevents a malformed cross-source duplicate reference from
    being counted twice; the first occurrence is selected by canonical source
    event order, never by input order.
    """

    grouped: dict[SourceEventKey, list[Mapping[str, Any]]] = defaultdict(list)
    for source, records in (("advisor", advisor_records), ("service-health", service_health_records)):
        for row in _rows(records):
            grouped[_identity(source, row)].append(row)

    events: list[SourceEvent] = []
    memberships: list[AggregateMembership] = []
    seen_refs: set[str] = set()
    for key in sorted(grouped):
        rows = tuple(sorted(grouped[key], key=lambda row: (_text(row.get("raw_record_ref")), _canonical(row))))
        selected_rows = tuple(
            row for row in rows if _text(row.get("raw_record_ref")) and _text(row.get("raw_record_ref")) not in seen_refs
        )
        refs = tuple(_text(row.get("raw_record_ref")) for row in selected_rows)
        if not refs:
            continue
        seen_refs.update(refs)
        event = SourceEvent(key, key.source, refs[0], selected_rows[0], selected_rows)
        events.append(event)
        memberships.append(AggregateMembership(key, refs))
    return tuple(events), tuple(memberships)


__all__ = [
    "AggregateId",
    "AggregateMembership",
    "SourceEvent",
    "SourceEventKey",
    "aggregate_id_for",
    "build_source_events",
]
