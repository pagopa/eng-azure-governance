"""Shared concurrency helpers for worker sizing decisions."""

from __future__ import annotations


def effective_worker_count(subscriptions_count: int, requested_workers: int | None) -> int:
    """Resolve a safe worker count bounded by available subscriptions."""
    if subscriptions_count <= 1:
        return 1
    if requested_workers is None:
        return min(16, subscriptions_count)
    return max(1, min(requested_workers, subscriptions_count))
