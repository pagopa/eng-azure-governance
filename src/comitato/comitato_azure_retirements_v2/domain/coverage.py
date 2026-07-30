from __future__ import annotations

from collections.abc import Mapping, Iterable

from .diagnostics import Diagnostic, ValidationResult
from .platforms import PlatformCatalogSnapshot, SubscriptionId


def validate_platform_coverage(
    scope_subscription_ids: Iterable[str],
    records: Iterable[Mapping[str, str]],
    catalog: PlatformCatalogSnapshot,
    *,
    report: str = "all",
    run_id: str = "",
) -> ValidationResult[tuple[str, ...]]:
    references: dict[str, set[str]] = {}
    required: set[str] = set()
    for raw_id in scope_subscription_ids:
        try:
            required.add(SubscriptionId(raw_id).value)
        except (ValueError, AttributeError):
            continue
    for record in records:
        raw_id = str(record.get("subscription_id", ""))
        if not raw_id:
            continue
        try:
            canonical = SubscriptionId(raw_id).value
        except (ValueError, AttributeError):
            continue
        required.add(canonical)
        references.setdefault(canonical, set()).add(str(record.get("raw_record_ref", "")))
    diagnostics: list[Diagnostic] = []
    for subscription_id in sorted(required):
        if catalog.lookup(subscription_id) is None:
            refs = tuple(sorted(ref for ref in references.get(subscription_id, set()) if ref))
            name = ""
            diagnostics.append(Diagnostic(
                "error", "platform_mapping_unmapped_subscription", "mapping", report, run_id,
                subscription_id=subscription_id,
                message=f"Publication blocked: subscription (name unavailable) ({subscription_id}) has no active assignment in src/_source_of_truth/eng-finops-platforms.yaml",
                context=(("subscription_name", name), ("record_refs", ",".join(refs))),
            ))
    if diagnostics:
        return ValidationResult.invalid(tuple(diagnostics))
    return ValidationResult.valid(tuple(sorted(required)))
