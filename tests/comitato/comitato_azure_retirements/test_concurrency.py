from __future__ import annotations

from src.comitato.comitato_azure_retirements.libs.concurrency import (
    effective_worker_count,
)


def test_effective_worker_count_returns_one_for_zero_or_one_subscription() -> None:
    assert effective_worker_count(0, None) == 1
    assert effective_worker_count(1, 8) == 1


def test_effective_worker_count_uses_default_cap_when_requested_workers_missing() -> None:
    assert effective_worker_count(3, None) == 3
    assert effective_worker_count(20, None) == 16


def test_effective_worker_count_respects_requested_bounds() -> None:
    assert effective_worker_count(8, 4) == 4
    assert effective_worker_count(8, 99) == 8
    assert effective_worker_count(8, 0) == 1
