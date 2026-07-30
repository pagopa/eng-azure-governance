from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .model import Artifact


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RawArtifactPair(Generic[T]):
    artifact: Artifact[T]


__all__ = ["RawArtifactPair"]
