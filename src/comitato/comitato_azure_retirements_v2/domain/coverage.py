from __future__ import annotations

from collections.abc import Iterable, Mapping

from .diagnostics import Diagnostic, ValidationResult
from .platforms import PlatformCatalogSnapshot, SubscriptionId


def validate_platform_coverage(
    scope_subscription_ids: Iterable[str] | object,
    records: Iterable[Mapping[str, str]] | object,
    catalog: PlatformCatalogSnapshot,
    *,
    report: str = "all",
    run_id: str = "",
) -> ValidationResult[tuple[str, ...]]:
    if hasattr(scope_subscription_ids, "subscription_ids"):
        scope_subscription_ids = getattr(scope_subscription_ids, "subscription_ids")
    references: dict[str, set[str]] = {}
    names: dict[str, set[str]] = {}
    required: set[str] = set()
    for raw_id in scope_subscription_ids:
        try:
            required.add(SubscriptionId(raw_id).value)
        except (ValueError, AttributeError):
            continue
    def rows(value: object) -> Iterable[Mapping[str, object]]:
        artifact = getattr(value, "artifact", None)
        if artifact is not None:
            yield from rows(artifact)
            return
        artifact_records = getattr(value, "records", None)
        if artifact_records is not None:
            yield from rows(artifact_records)
            return
        if isinstance(value, Mapping):
            yield value
            return
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            for item in value:
                yield from rows(item)

    for record in rows(records):
        raw_id = str(record.get("subscription_id", ""))
        if not raw_id:
            continue
        try:
            canonical = SubscriptionId(raw_id).value
        except (ValueError, AttributeError):
            continue
        required.add(canonical)
        references.setdefault(canonical, set()).add(str(record.get("raw_record_ref", "")))
        name = str(record.get("subscription_name", "")).strip()
        if name:
            names.setdefault(canonical, set()).add(name)
    diagnostics: list[Diagnostic] = []
    for subscription_id in sorted(required):
        if catalog.lookup(subscription_id) is None:
            refs = tuple(sorted(ref for ref in references.get(subscription_id, set()) if ref))
            name_candidates = sorted(
                names.get(subscription_id, ()), key=lambda value: (value.casefold(), value)
            )
            display_name = name_candidates[0] if name_candidates else "(name unavailable)"
            refs = tuple(sorted(ref for ref in references.get(subscription_id, set()) if ref))
            diagnostics.append(Diagnostic(
                "error", "platform_mapping_unmapped_subscription", "mapping", report, run_id,
                subscription_id=subscription_id,
                message=f"Publication blocked: subscription {display_name} ({subscription_id}) has no active assignment in src/_source_of_truth/eng-finops-platforms.yaml",
                context=(
                    ("subscription_name", "" if not name_candidates else name_candidates[0]),
                    ("record_refs", ",".join(refs)),
                ),
            ))
    if diagnostics:
        return ValidationResult.invalid(tuple(diagnostics))
    return ValidationResult.valid(tuple(sorted(required)))
