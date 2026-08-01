from __future__ import annotations

from dataclasses import dataclass

from ..contracts.aggregate_v1 import AGGREGATE_V1
from ..contracts.model import Artifact
from ..contracts.slides_v1 import SLIDES_V1, SlideRecord
from .dates import CommitteeWindow, SlideEligibility, classify_retirement_date
from .diagnostics import Diagnostic, ValidationResult


@dataclass(frozen=True, slots=True)
class SlideSelection:
    artifact: Artifact
    excluded_by_reason: dict[str, tuple[str, ...]]


def select_slides(aggregate: Artifact, context) -> ValidationResult[SlideSelection]:
    if aggregate.contract != AGGREGATE_V1.name or aggregate.schema_version != AGGREGATE_V1.schema_version:
        return ValidationResult.invalid(
            (
                Diagnostic(
                    "error", "invalid_aggregate_input", "slides", "slides", context.run_id
                ),
            )
        )
    if aggregate.run_id != context.run_id:
        return ValidationResult.invalid(
            (
                Diagnostic(
                    "error", "aggregate_context_mismatch", "slides", "slides", context.run_id
                ),
            )
        )

    window = CommitteeWindow(context.as_of_date)
    selected = []
    excluded: dict[str, list[str]] = {}
    for row in aggregate.records:
        eligibility = classify_retirement_date(row, window)
        if eligibility is SlideEligibility.ELIGIBLE:
            selected.append(SlideRecord.from_aggregate(row, aggregate.schema_version))
        else:
            excluded.setdefault(eligibility.value, []).append(row["aggregate_id"])
    selected.sort(key=lambda row: (row["retirement_date"], row["aggregate_id"]))
    result = Artifact(
        contract=SLIDES_V1.name,
        schema_version=SLIDES_V1.schema_version,
        run_id=context.run_id,
        records=tuple(selected),
    )
    checked = SLIDES_V1.validate(result, context)
    if not checked.is_valid:
        return ValidationResult.invalid(checked.diagnostics)
    return ValidationResult.valid(
        SlideSelection(
            artifact=result,
            excluded_by_reason={key: tuple(sorted(value)) for key, value in sorted(excluded.items())},
        )
    )


def project_slides(aggregate: Artifact, context) -> ValidationResult[Artifact]:
    result = select_slides(aggregate, context)
    if not result.is_valid or result.value is None:
        return ValidationResult.invalid(result.diagnostics)
    return ValidationResult.valid(result.value.artifact)


__all__ = ["SlideSelection", "project_slides", "select_slides"]
