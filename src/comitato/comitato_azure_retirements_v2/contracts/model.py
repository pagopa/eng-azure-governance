from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Generic, Mapping, Protocol, TypeVar

from ..domain.diagnostics import ValidationResult
from ..domain.execution import RunContext


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Artifact(Generic[T]):
    contract: str
    schema_version: int
    run_id: str
    records: tuple[T, ...] = ()
    companion_records: tuple[Any, ...] = ()


@dataclass(frozen=True, slots=True)
class EncodedArtifact:
    logical_path: str
    data: bytes
    rows: int
    media_type: str
    schema_version: int
    run_id: str

    @property
    def path(self) -> str:
        return self.logical_path

    @property
    def bytes(self) -> int:
        return len(self.data)

    @property
    def digest(self) -> str:
        return sha256(self.data).hexdigest()


class Contract(Protocol[T]):
    name: str
    header: tuple[str, ...]
    path: str
    schema_version: int

    def empty_artifact(self, context: RunContext) -> Artifact[T]:
        ...

    def encode(self, artifact: Artifact[T]) -> EncodedArtifact:
        ...

    def decode(self, data: bytes) -> Artifact[Mapping[str, str]]:
        ...

    def validate(
        self, artifact: Artifact[T], context: RunContext
    ) -> ValidationResult[Artifact[T]]:
        ...
