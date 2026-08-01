from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Mapping, TypeVar

from ..domain.diagnostics import ValidationResult
from ..domain.execution import RunContext
from .codecs import decode_jsonl, decode_tsv, encode_jsonl, encode_tsv
from .model import Artifact, EncodedArtifact


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class TsvContract(Generic[T]):
    name: str
    header: tuple[str, ...]
    path: str
    companion_path: str | None = None
    schema_version: int = 1

    def empty_artifact(self, context: RunContext) -> Artifact[T]:
        return Artifact(
            contract=self.name,
            schema_version=self.schema_version,
            run_id=context.run_id,
        )

    def encode(self, artifact: Artifact[T]) -> EncodedArtifact:
        return EncodedArtifact(
            logical_path=self.path,
            data=encode_tsv(self.header, artifact.records),
            rows=len(artifact.records),
            media_type="text/tab-separated-values",
            schema_version=self.schema_version,
            run_id=artifact.run_id,
        )

    def encode_companion(self, artifact: Artifact[T]) -> EncodedArtifact:
        if self.companion_path is None:
            raise ValueError(f"{self.name} has no JSONL companion")
        return EncodedArtifact(
            logical_path=self.companion_path,
            data=encode_jsonl(artifact.companion_records),
            rows=len(artifact.companion_records),
            media_type="application/x-ndjson",
            schema_version=self.schema_version,
            run_id=artifact.run_id,
        )

    def decode(self, data: bytes) -> Artifact[Mapping[str, str]]:
        records = decode_tsv(data, self.header)
        return Artifact(
            contract=self.name,
            schema_version=self.schema_version,
            run_id=records[0].get("run_id", "") if records else "",
            records=records,
        )

    def decode_companion(self, data: bytes) -> tuple[Any, ...]:
        if self.companion_path is None:
            raise ValueError(f"{self.name} has no JSONL companion")
        return decode_jsonl(data)

    def validate(
        self, artifact: Artifact[T], context: RunContext
    ) -> ValidationResult[Artifact[T]]:
        if artifact.contract != self.name or artifact.schema_version != self.schema_version:
            raise ValueError("artifact does not belong to this contract")
        if artifact.run_id != context.run_id:
            raise ValueError("artifact run_id does not match context")
        return ValidationResult.valid(artifact)
