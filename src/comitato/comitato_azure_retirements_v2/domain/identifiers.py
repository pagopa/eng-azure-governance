"""Validated source identifiers and canonical comparison helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SubscriptionId:
    exact: str

    def __post_init__(self) -> None:
        value = self.exact.strip()
        if not value:
            raise ValueError("subscription ID must not be empty")
        try:
            UUID(value)
        except ValueError as exc:
            raise ValueError(f"invalid subscription UUID: {self.exact}") from exc

    @property
    def normalized(self) -> str:
        return self.exact.casefold()


@dataclass(frozen=True, slots=True)
class ArmResourceId:
    exact: str

    def __post_init__(self) -> None:
        value = self.exact.strip()
        if not value or not value.startswith("/"):
            raise ValueError("ARM resource ID must be an absolute path")
        if "//" in value:
            raise ValueError("ARM resource ID contains repeated separators")

    @property
    def normalized(self) -> str:
        return re.sub(r"/+", "/", self.exact.strip()).casefold().rstrip("/")


@dataclass(frozen=True, slots=True)
class SourceIdentity:
    exact: str

    def __post_init__(self) -> None:
        if not self.exact.strip():
            raise ValueError("source identity must not be empty")

    @property
    def normalized(self) -> str:
        return self.exact.strip().casefold()


__all__ = ["ArmResourceId", "SourceIdentity", "SubscriptionId"]
