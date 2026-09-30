from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .evidence import SourcePage, SourceRecord
from .model import AcquisitionReceipt, SourceAcquisition


class AcquisitionIntegrityError(ValueError):
    """The acquired page stream cannot prove complete, lossless evidence."""


@dataclass(frozen=True, slots=True)
class ScriptedRequest:
    subscription_id: str
    pages: tuple[SourcePage, ...]
    complete: bool = True


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def collect_complete_pages(
    requests: Sequence[ScriptedRequest],
    identity_of: Callable[[Mapping[str, Any]], str],
) -> SourceAcquisition:
    """Collect complete scripted pages with deterministic identity integrity."""
    records: dict[tuple[str, str], SourceRecord] = {}
    pages_seen = 0
    for request in requests:
        seen_tokens: set[str] = set()
        for page_number, page in enumerate(request.pages, start=1):
            if page.subscription_id != request.subscription_id:
                raise AcquisitionIntegrityError(
                    "page subscription does not match scripted request"
                )
            pages_seen += 1
            token = page.continuation_token
            if token is not None:
                if token in seen_tokens:
                    raise AcquisitionIntegrityError(
                        f"repeated continuation token: {token}"
                    )
                seen_tokens.add(token)
            for payload in page.items:
                identity = str(identity_of(payload)).strip()
                if not identity:
                    raise AcquisitionIntegrityError("source record identity is empty")
                key = (request.subscription_id, identity)
                candidate = SourceRecord(
                    request.subscription_id,
                    identity,
                    payload,
                    source="scripted",
                    page_number=page_number,
                    continuation_token=token,
                )
                existing = records.get(key)
                if existing is None:
                    records[key] = candidate
                elif _canonical(existing.payload) != _canonical(payload):
                    raise AcquisitionIntegrityError(
                        f"conflicting payload for identity: {identity}"
                    )

    ordered = tuple(
        sorted(
            records.values(),
            key=lambda record: (
                record.subscription_id.casefold(),
                record.identity.casefold(),
                record.subscription_id,
                record.identity,
            ),
        )
    )
    receipt = AcquisitionReceipt(
        source="scripted",
        api_version="scripted-v1",
        expected_subscriptions=len(requests),
        completed_subscriptions=sum(request.complete for request in requests),
        pages=pages_seen,
        source_records=len(ordered),
        complete=all(request.complete for request in requests),
        continuation_tokens=tuple(
            page.continuation_token
            for request in requests
            for page in request.pages
            if page.continuation_token is not None
        ),
        failed_subscriptions=tuple(
            request.subscription_id for request in requests if not request.complete
        ),
    )
    return SourceAcquisition(receipt=receipt, records=ordered)


__all__ = [
    "AcquisitionIntegrityError",
    "ScriptedRequest",
    "SourcePage",
    "SourceRecord",
    "collect_complete_pages",
]
