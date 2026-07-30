from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from typing import Any, Mapping

from ..acquisition.model import SourceAcquisition
from ..contracts.model import Artifact
from ..contracts.raw_pair import RawArtifactPair
from ..contracts.service_health_v1 import SERVICE_HEALTH_V1
from ..domain.diagnostics import Diagnostic, ValidationResult
from ..domain.execution import RunContext


@dataclass(frozen=True, slots=True)
class ServiceHealthSupplementalEvidence:
    advisor_records: tuple[Mapping[str, Any], ...] = ()
    resource_inventory: Mapping[str, Mapping[str, Any]] = ()
    subscription_inventory: Mapping[str, Mapping[str, Any]] = ()


class _ArticleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in {"p", "div", "li", "br", "h1", "h2", "h3"}:
            self.parts.append(" ")
        if tag.casefold() == "a":
            self.href = dict(attrs).get("href")

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "a" and self.href:
            self.parts.append(f" ({self.href})")
            self.href = None
        elif tag.casefold() in {"p", "div", "li", "br", "h1", "h2", "h3"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _timestamp(value: Any) -> tuple[str, str]:
    raw = "" if value is None else str(value)
    if not raw:
        return "", ""
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"), ""
    except ValueError:
        return "", "invalid_timestamp"


def _date(raw: Any) -> tuple[str, str]:
    value = "" if raw is None else str(raw)
    if not value:
        return "", "missing"
    try:
        return value[:10], "exact"
    except (TypeError, ValueError):
        return "", "invalid"


def _plain_article(value: Any) -> str:
    parser = _ArticleParser()
    parser.feed(html.unescape(str(value or "")))
    return re.sub(r"\s+", " ", "".join(parser.parts)).strip()


def _resource_parts(value: str) -> tuple[str, str, str]:
    segments = [part for part in value.split("/") if part]
    lowered = [part.casefold() for part in segments]
    group = ""
    resource_type = ""
    name = ""
    if "resourcegroups" in lowered:
        index = lowered.index("resourcegroups")
        group = segments[index + 1] if index + 1 < len(segments) else ""
    if "providers" in lowered:
        index = lowered.index("providers")
        resource_type = "/".join(segments[index + 1 : index + 3])
        name = segments[index + 3] if index + 3 < len(segments) else ""
    return name, group, resource_type


def _payload(record: Any) -> Mapping[str, Any]:
    value = getattr(record, "payload", record)
    return _mapping(value)


def normalize_service_health(
    acquisition: SourceAcquisition,
    context: RunContext,
    evidence: ServiceHealthSupplementalEvidence,
) -> ValidationResult[RawArtifactPair[Mapping[str, str]]]:
    rows: list[dict[str, str]] = []
    companions: list[dict[str, Any]] = []
    diagnostics: list[Diagnostic] = []
    for raw_record in acquisition.records:
        event = _payload(raw_record)
        props = _mapping(event.get("properties"))
        event_id = str(event.get("id") or "")
        event_name = str(event.get("name") or "")
        event_type = str(props.get("eventType") or "")
        level = str(props.get("level") or "")
        status = str(props.get("status") or "")
        if event_type.casefold() != "healthadvisory" or level.casefold() not in {"warning", "critical"} or status.casefold() != "active":
            if not event_type or not level or not status:
                diagnostics.append(Diagnostic("error", "invalid_service_health_classification", "normalization", "service-health", context.run_id, record_ref=event_id))
            continue
        tracking = str(props.get("trackingId") or event_name)
        if props.get("trackingId") and event_name and tracking.casefold() != event_name.casefold() and str(props.get("trackingId")).casefold() != tracking.casefold():
            diagnostics.append(Diagnostic("error", "tracking_id_mismatch", "normalization", "service-health", context.run_id, record_ref=event_id))
            continue
        article = _mapping(props.get("article"))
        raw_article = article.get("articleContent") or props.get("description")
        description = _plain_article(raw_article)
        description_quality = "full_article" if article.get("articleContent") else "description_fallback" if props.get("description") else "missing"
        start, start_flag = _timestamp(props.get("impactStartTime"))
        mitigation, mitigation_flag = _timestamp(props.get("impactMitigationTime"))
        last_update, update_flag = _timestamp(props.get("lastUpdateTime"))
        retirement_raw = str(props.get("impactMitigationTime") or "")
        retirement_date, retirement_quality = _date(retirement_raw)
        flags = set(filter(None, (start_flag, mitigation_flag, update_flag)))
        if retirement_quality == "missing":
            flags.add("missing_retirement_date")
        services = props.get("impactedServices") or ()
        associations: list[tuple[str, str, str, str, str]] = []
        for service in services:
            service_map = _mapping(service)
            service_name = str(service_map.get("serviceName") or "")
            service_guid = str(service_map.get("serviceGuid") or "")
            for region in service_map.get("impactedRegions") or ():
                region_map = _mapping(region)
                region_name = str(region_map.get("regionName") or region_map.get("regionId") or "")
                associations.append((service_name, service_guid, region_name, "", ""))
        resources = props.get("impactedResources") or ()
        if resources:
            associations = [(service, guid, region, str(_mapping(resource).get("subscriptionId") or ""), str(_mapping(resource).get("resourceId") or "")) for resource in resources for service, guid, region, _, _ in (associations or [("", "", "", "", "")])]
        if not associations:
            associations = [("", "", "", "", "")]
        for service_name, service_guid, region, affected_subscription, resource_id in associations:
            collection_subscription = str(event.get("subscriptionId") or "")
            subscription_id = affected_subscription or collection_subscription
            if not subscription_id and str(props.get("isGlobal") or "").casefold() != "true":
                diagnostics.append(Diagnostic("error", "missing_affected_subscription", "normalization", "service-health", context.run_id, record_ref=event_id))
                continue
            normalized_resource = re.sub(r"/+", "/", resource_id.strip()).casefold().rstrip("/") if resource_id else ""
            name, group, resource_type = _resource_parts(resource_id)
            record_type = "service_health_event_resource" if resource_id else "service_health_event_service_region" if service_name or region else "service_health_event_subscription"
            if not resource_id:
                flags.add("resource_not_published")
            ref = sha256(f"{context.run_id}\0{event_id}\0{subscription_id}\0{resource_id}\0{service_name}\0{region}".encode()).hexdigest()
            row: dict[str, str] = {column: "" for column in SERVICE_HEALTH_V1.header}
            row.update({
                "schema_version": "1", "run_id": context.run_id, "as_of_date": context.as_of_date.isoformat(), "scope_mode": context.scope.mode,
                "record_type": record_type, "source_system": "azure_service_health", "service_health_event_id": event_id, "event_name": event_name, "tracking_id": tracking,
                "collection_subscription_id": collection_subscription, "subscription_id": subscription_id, "event_type": event_type, "event_sub_type": str(props.get("eventSubType") or ""), "event_source": str(props.get("eventSource") or ""),
                "event_level": level, "status": status, "title": str(props.get("title") or ""), "summary": str(props.get("summary") or ""), "description_problem": description,
                "description_quality": description_quality, "recommended_actions": str(props.get("recommendedActions") or ""), "impact_start_time_raw": str(props.get("impactStartTime") or ""), "impact_start_time": start,
                "impact_mitigation_time_raw": str(props.get("impactMitigationTime") or ""), "impact_mitigation_time": mitigation, "last_update_time_raw": str(props.get("lastUpdateTime") or ""), "last_update_time": last_update,
                "retirement_date_raw": retirement_raw, "retirement_date": retirement_date, "retirement_date_source": "properties.impactMitigationTime" if retirement_raw else "", "retirement_date_quality": retirement_quality,
                "impacted_service": service_name, "impacted_service_guid": service_guid, "impacted_region": region, "normalized_impacted_region": region.casefold(), "resource_evidence_source": "service_health_resource" if resource_id else "none",
                "resource_evidence_status": "published" if resource_id else "not_published", "published_resource_id": resource_id, "normalized_resource_id": normalized_resource, "resource_name": name, "resource_group": group, "resource_type": resource_type,
                "resource_location": "", "is_sensitive": "false", "details_fetch_status": "not_needed", "diagnostic_flags": ",".join(sorted(flags)),
                "provenance_json": _canonical({"api_version": acquisition.receipt.api_version, "event_id": event_id, "association": record_type}), "raw_record_ref": ref,
            })
            rows.append(row)
            companions.append({"schema_version": 1, "run_id": context.run_id, "raw_record_ref": ref, "service_health_event": event, "collection_subscription_id": collection_subscription, "affected_subscription_id": subscription_id, "service_health_resource_evidence": {"resourceId": resource_id} if resource_id else None, "advisor_evidence": None, "resource_inventory": None, "subscription_inventory": None})
    if diagnostics:
        return ValidationResult.invalid(tuple(diagnostics))
    rows.sort(key=lambda row: (row["collection_subscription_id"].casefold(), row["service_health_event_id"].casefold(), row["subscription_id"].casefold(), row["record_type"], row["normalized_resource_id"].casefold(), row["impacted_service"].casefold(), row["normalized_impacted_region"], row["resource_evidence_source"]))
    companion_by_ref = {item["raw_record_ref"]: item for item in companions}
    artifact = Artifact("service-health", 1, context.run_id, tuple(rows), tuple(companion_by_ref[row["raw_record_ref"]] for row in rows))
    return ValidationResult.valid(RawArtifactPair(artifact))


__all__ = ["ServiceHealthSupplementalEvidence", "normalize_service_health"]
