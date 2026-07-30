from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar


@dataclass(frozen=True, slots=True)
class Diagnostic:
    severity: str
    code: str
    stage: str
    report: str
    run_id: str
    subscription_id: str = ""
    record_ref: str = ""
    artifact: str = ""
    message: str = ""
    context: tuple[tuple[str, str], ...] = ()

    def sort_key(self) -> tuple[str, str, str, str, str]:
        return (
            self.stage,
            self.code,
            self.subscription_id,
            self.record_ref,
            self.artifact,
        )

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "severity": self.severity,
            "code": self.code,
            "stage": self.stage,
            "report": self.report,
            "run_id": self.run_id,
            "subscription_id": self.subscription_id,
            "record_ref": self.record_ref,
            "artifact": self.artifact,
            "message": self.message,
        }
        context = dict(self.context)
        if self.code == "platform_mapping_unmapped_subscription":
            payload["subscription_name"] = context.get("subscription_name", "")
            refs = context.get("record_refs", "")
            payload["record_refs"] = [item for item in refs.split(",") if item]
        return payload


def sort_diagnostics(
    diagnostics: tuple[Diagnostic, ...] | list[Diagnostic],
) -> tuple[Diagnostic, ...]:
    return tuple(sorted(diagnostics, key=Diagnostic.sort_key))


T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ValidationResult(Generic[T]):
    value: T | None
    diagnostics: tuple[Diagnostic, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not self.diagnostics

    @classmethod
    def valid(cls, value: T) -> "ValidationResult[T]":
        return cls(value=value)

    @classmethod
    def invalid(cls, diagnostics: tuple[Diagnostic, ...]) -> "ValidationResult[T]":
        if not diagnostics:
            raise ValueError("invalid validation result needs diagnostics")
        return cls(value=None, diagnostics=sort_diagnostics(diagnostics))
