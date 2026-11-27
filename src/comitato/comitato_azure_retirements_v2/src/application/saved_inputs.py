from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from typing import Any

from ..acquisition.evidence import ObservationAccounting, SourceRecord
from ..acquisition.model import AcquisitionReceipt, SourceAcquisition
from ..domain.evidence import AdvisorEnrichments, ServiceHealthSupplementalEvidence
from ..domain.execution import ReportSelector
from ..domain.platforms import (
    PlatformAssignment,
    PlatformCatalogSnapshot,
    SubscriptionId,
)


def json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def saved_acquisition(acquisition: SourceAcquisition) -> dict[str, Any]:
    return {
        "receipt": json_safe(acquisition.receipt),
        "records": json_safe(acquisition.records),
        "companion_records": json_safe(acquisition.companion_records),
        "accounting": json_safe(acquisition.accounting),
        "collection_context": json_safe(acquisition.collection_context),
        "response_context": json_safe(acquisition.response_context),
    }


def _source_yaml(source: Any) -> str:
    source_path = getattr(source, "path", None)
    if source_path is None:
        return ""
    try:
        return source_path.read_text(encoding="utf-8")
    except OSError:
        return ""


def saved_catalog(catalog: Any, source: Any = None) -> dict[str, Any]:
    assignments = []
    for assignment in getattr(catalog, "assignments", ()):
        assignments.append(
            {
                "subscription_id": str(
                    getattr(getattr(assignment, "subscription_id", None), "value", "")
                ),
                "platform": str(getattr(assignment, "platform", "")),
                "subscription_name": str(getattr(assignment, "subscription_name", "")),
            }
        )
    return {
        "schema_version": int(getattr(catalog, "schema_version", 1)),
        "sha256": str(getattr(catalog, "sha256", "")),
        "assignments": assignments,
        "yaml": _source_yaml(source),
    }


def saved_service_health_evidence(
    evidence: ServiceHealthSupplementalEvidence,
) -> dict[str, Any]:
    return {
        "advisor_records": json_safe(evidence.advisor_records),
        "resource_inventory": json_safe(evidence.resource_inventory),
        "subscription_inventory": json_safe(evidence.subscription_inventory),
        "resource_associations": [
            {
                "tracking_id": key[0],
                "subscription_id": key[1],
                "resources": json_safe(values),
            }
            for key, values in sorted(evidence.resource_associations.items())
        ],
        "subscription_name_sources": json_safe(evidence.subscription_name_sources),
    }


def catalog_from_saved_inputs(
    saved_inputs: Mapping[str, Any],
) -> PlatformCatalogSnapshot:
    payload = saved_inputs.get("platform_catalog")
    if not isinstance(payload, Mapping) or not isinstance(
        payload.get("assignments"), list
    ):
        raise ValueError("replay bundle is missing saved platform catalog")
    assignments = tuple(
        PlatformAssignment(
            SubscriptionId(str(item["subscription_id"])),
            str(item["platform"]),
            str(item["subscription_name"]),
        )
        for item in payload["assignments"]
        if isinstance(item, Mapping)
    )
    return PlatformCatalogSnapshot(
        int(payload["schema_version"]), str(payload["sha256"]), assignments
    )


def acquisitions_from_saved_inputs(
    saved_inputs: Mapping[str, Any],
    closure: Any,
) -> dict[str, SourceAcquisition]:
    payload = saved_inputs.get("source_acquisitions")
    if not isinstance(payload, Mapping):
        raise ValueError("replay bundle is missing saved acquisitions")
    result: dict[str, SourceAcquisition] = {}
    required = []
    if closure.requires(ReportSelector.ADVISOR):
        required.append("advisor")
    if closure.requires(ReportSelector.SERVICE_HEALTH):
        required.append("service-health")
    for source in required:
        item = payload.get(source)
        if not isinstance(item, Mapping) or not isinstance(
            item.get("receipt"), Mapping
        ):
            raise ValueError(f"replay bundle is missing saved {source} acquisition")
        receipt_payload = item["receipt"]
        receipt = AcquisitionReceipt(
            source=str(receipt_payload["source"]),
            api_version=str(receipt_payload["api_version"]),
            expected_subscriptions=int(receipt_payload["expected_subscriptions"]),
            completed_subscriptions=int(receipt_payload["completed_subscriptions"]),
            pages=int(receipt_payload["pages"]),
            source_records=int(receipt_payload["source_records"]),
            complete=bool(receipt_payload["complete"]),
            continuation_tokens=tuple(
                str(value) for value in receipt_payload.get("continuation_tokens", ())
            ),
            failed_subscriptions=tuple(
                str(value) for value in receipt_payload.get("failed_subscriptions", ())
            ),
            completeness_reason=str(receipt_payload.get("completeness_reason", "")),
        )
        accounting = tuple(
            ObservationAccounting(
                source=str(value["source"]),
                subscription_id=str(value["subscription_id"]),
                source_identity=str(value["source_identity"]),
                destination=str(value["destination"]),
                reason=str(value.get("reason", "")),
                raw_record_ref=str(value.get("raw_record_ref", "")),
            )
            for value in item.get("accounting", ())
            if isinstance(value, Mapping)
        )
        result[source] = SourceAcquisition(
            receipt=receipt,
            records=tuple(_source_record(value) for value in item.get("records", ())),
            companion_records=tuple(item.get("companion_records", ())),
            accounting=accounting,
            collection_context=item.get("collection_context", {}),
            response_context=tuple(item.get("response_context", ())),
        )
    return result


def _source_record(value: Any) -> Any:
    if not isinstance(value, Mapping) or not isinstance(value.get("payload"), Mapping):
        return value
    return SourceRecord(
        subscription_id=str(value.get("subscription_id", "")),
        identity=str(value.get("identity", "")),
        payload=value["payload"],
        source=str(value.get("source", "")),
        page_number=int(value.get("page_number", 0)),
        continuation_token=value.get("continuation_token"),
    )


def advisor_enrichments_from_saved_inputs(
    saved_inputs: Mapping[str, Any],
) -> AdvisorEnrichments:
    payload = saved_inputs.get("advisor_enrichments", {})
    if not isinstance(payload, Mapping):
        raise ValueError("replay bundle has invalid Advisor enrichment inputs")
    return AdvisorEnrichments(
        metadata=payload.get("metadata", {}),
        resources=payload.get("resources", {}),
        subscriptions=payload.get("subscriptions", {}),
    )


def service_health_evidence_from_saved_inputs(
    saved_inputs: Mapping[str, Any],
) -> ServiceHealthSupplementalEvidence:
    payload = saved_inputs.get("service_health_evidence", {})
    if not isinstance(payload, Mapping):
        raise ValueError("replay bundle has invalid Service Health evidence inputs")
    associations = {
        (
            str(item["tracking_id"]).casefold(),
            str(item["subscription_id"]).casefold(),
        ): tuple(item.get("resources", ()))
        for item in payload.get("resource_associations", ())
        if isinstance(item, Mapping)
    }
    return ServiceHealthSupplementalEvidence(
        advisor_records=tuple(payload.get("advisor_records", ())),
        resource_inventory=payload.get("resource_inventory", {}),
        subscription_inventory=payload.get("subscription_inventory", {}),
        resource_associations=associations,
        subscription_name_sources=payload.get("subscription_name_sources", {}),
    )


__all__ = [
    "acquisitions_from_saved_inputs",
    "advisor_enrichments_from_saved_inputs",
    "catalog_from_saved_inputs",
    "json_safe",
    "saved_acquisition",
    "saved_catalog",
    "saved_service_health_evidence",
    "service_health_evidence_from_saved_inputs",
]
