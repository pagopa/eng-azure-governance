from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from ..domain.execution import RunRequest, Scope


@dataclass(frozen=True, slots=True)
class FixedSubscriptionScopeSource:
    subscription_ids: tuple[str, ...]
    mode: str = "explicit"

    def resolve(self, request: RunRequest) -> Scope:
        canonical = tuple(sorted({str(UUID(item)).lower() for item in self.subscription_ids}))
        return Scope(subscription_ids=canonical, mode=self.mode)


__all__ = ["FixedSubscriptionScopeSource"]
