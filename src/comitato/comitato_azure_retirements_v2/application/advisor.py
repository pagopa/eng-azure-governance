from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
from typing import Any, Mapping

from ..acquisition.model import SourceAcquisition
from ..contracts.advisor_v1 import ADVISOR_V1
from ..contracts.model import Artifact
from ..contracts.raw_pair import RawArtifactPair
from ..domain.diagnostics import Diagnostic, ValidationResult
from ..domain.execution import RunContext


@dataclass(frozen=True, slots=True)
class AdvisorEnrichments:
    metadata: Mapping[str, Mapping[str, Any]] = ()
    resources: Mapping[str, Mapping[str, Any]] = ()
    subscriptions: Mapping[str, Mapping[str, Any]] = ()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _normalized_arm(value: str) -> str:
    return re.sub(r"/+", "/", value.strip()).casefold().rstrip("/")


def _date_value(value: Any) -> tuple[str, str]:
    raw = "" if value is None else str(value)
    if not raw:
        return "", "missing"
    try:
        parsed = date.fromisoformat(raw[:10])
    except ValueError:
        return "", "invalid"
    return parsed.isoformat(), "exact"


def _timestamp(value: Any) -> str:
    raw = "" if value is None else str(value)
    if not raw:
        return ""
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        return raw


def _subscription_id(record: Mapping[str, Any], recommendation_id: str) -> str:
    direct = record.get("subscriptionId") or record.get("subscription_id")
    if direct:
        return str(direct)
    match = re.search(r"/subscriptions/([^/]+)", recommendation_id, re.IGNORECASE)
    return match.group(1) if match else ""


def _resource_parts(resource_id: str) -> tuple[str, str, str]:
    segments = [part for part in resource_id.split("/") if part]
    lowered = [part.casefold() for part in segments]
    group = ""
    resource_type = ""
    name = ""
    if "resourcegroups" in lowered:
        index = lowered.index("resourcegroups")
        if index + 1 < len(segments):
            group = segments[index + 1]
    if "providers" in lowered:
        index = lowered.index("providers")
        if index + 2 < len(segments):
            resource_type = f"{segments[index + 1]}/{segments[index + 2]}"
            name = segments[index + 3] if index + 3 < len(segments) else ""
    return name, group, resource_type


def _record_payload(record: Any) -> Mapping[str, Any]:
    payload = getattr(record, "payload", record)
    return _mapping(payload)


def normalize_advisor(
    acquisition: SourceAcquisition,
    context: RunContext,
    enrichments: AdvisorEnrichments,
) -> ValidationResult[RawArtifactPair[Mapping[str, str]]]:
    rows: list[dict[str, str]] = []
    companions: list[dict[str, Any]] = []
    diagnostics: list[Diagnostic] = []
    for raw_record in acquisition.records:
        recommendation = _record_payload(raw_record)
        properties = _mapping(recommendation.get("properties"))
        recommendation_id = str(
            recommendation.get("id") or recommendation.get("advisorRecommendationId") or ""
        )
        status = str(properties.get("recommendationStatus") or "")
        if status.casefold() != "new":
            if not status or status.casefold() not in {"inprogress", "completed", "postponed", "dismissed"}:
                diagnostics.append(Diagnostic("error", "invalid_recommendation_status", "normalization", "advisor", context.run_id, record_ref=recommendation_id))
            continue
        subscription_id = _subscription_id(recommendation, recommendation_id)
        metadata = _mapping(properties.get("resourceMetadata"))
        published = str(metadata.get("resourceId") or metadata.get("resource_id") or "")
        linkage = "resource_id"
        if not published:
            published = str(metadata.get("id") or "")
            linkage = "legacy_id" if published else "missing"
        normalized = _normalized_arm(published) if published else ""
        name, group, resource_type = _resource_parts(published)
        retirement_raw = properties.get("retirementDate") or properties.get("retirement_date")
        retirement_date, retirement_quality = _date_value(retirement_raw)
        flags: set[str] = set()
        if not published:
            flags.add("missing_published_resource_id")
        if linkage == "legacy_id":
            flags.add("legacy_resource_id_used")
        if retirement_quality == "missing":
            flags.add("missing_retirement_date")
        if retirement_quality == "invalid":
            flags.add("invalid_retirement_date")
        short_description = _mapping(properties.get("shortDescription"))
        description = str(properties.get("description") or "")
        if not description and not short_description.get("problem"):
            flags.add("missing_description")
        ref = sha256(f"{context.run_id}\0{recommendation_id}".encode()).hexdigest()
        row: dict[str, str] = {column: "" for column in ADVISOR_V1.header}
        row.update(
            {
                "schema_version": "1",
                "run_id": context.run_id,
                "as_of_date": context.as_of_date.isoformat(),
                "scope_mode": context.scope.mode,
                "record_type": "advisor_retirement_recommendation",
                "source_system": "azure_advisor",
                "advisor_recommendation_id": recommendation_id,
                "recommendation_type_id": str(properties.get("recommendationTypeId") or ""),
                "recommendation_status": status,
                "subscription_id": subscription_id,
                "resource_linkage_source": linkage,
                "published_resource_id": published,
                "normalized_resource_id": normalized,
                "resource_name": name,
                "resource_group": group,
                "resource_type": resource_type,
                "retirement_date_raw": str(retirement_raw or ""),
                "retirement_date": retirement_date,
                "retirement_date_source": "properties.retirementDate" if retirement_raw else "",
                "retirement_date_quality": retirement_quality,
                "impact": str(properties.get("impact") or ""),
                "risk": str(properties.get("risk") or ""),
                "category": str(properties.get("category") or ""),
                "sub_category": str(properties.get("subcategory") or properties.get("subCategory") or ""),
                "last_updated": _timestamp(properties.get("lastUpdated") or properties.get("lastUpdatedTime")),
                "label": str(properties.get("label") or ""),
                "short_description_problem": str(short_description.get("problem") or ""),
                "short_description_solution": str(short_description.get("solution") or ""),
                "description": description,
                "potential_benefits": str(properties.get("potentialBenefits") or ""),
                "learn_more_link": str(properties.get("learnMoreLink") or ""),
                "actions_json": _canonical(properties.get("actions") or []),
                "metadata_match_status": "missing",
                "resource_inventory_match_status": "missing",
                "subscription_inventory_match_status": "missing",
                "diagnostic_flags": ",".join(sorted(flags)),
                "provenance_json": _canonical({"recommendation_id": recommendation_id, "resource_linkage": linkage, "api_version": acquisition.receipt.api_version}),
                "raw_record_ref": ref,
            }
        )
        rows.append(row)
        companions.append(
            {
                "schema_version": 1,
                "run_id": context.run_id,
                "raw_record_ref": ref,
                "advisor_recommendation_id": recommendation_id,
                "recommendation": recommendation,
                "advisor_metadata": None,
                "resource_inventory": None,
                "subscription_inventory": None,
            }
        )
    if diagnostics:
        return ValidationResult.invalid(tuple(diagnostics))
    ordered = tuple(sorted(rows, key=lambda row: (row["subscription_id"].casefold(), row["advisor_recommendation_id"].casefold(), row["normalized_resource_id"].casefold(), row["recommendation_type_id"].casefold())))
    by_ref = {item["raw_record_ref"]: item for item in companions}
    ordered_companions = tuple(by_ref[row["raw_record_ref"]] for row in ordered)
    artifact = Artifact("advisor", 1, context.run_id, ordered, ordered_companions)
    return ValidationResult.valid(RawArtifactPair(artifact))


__all__ = ["AdvisorEnrichments", "normalize_advisor"]
