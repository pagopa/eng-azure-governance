from __future__ import annotations

import json
import re
from collections.abc import Mapping
from datetime import date, datetime, timezone
from hashlib import sha256
from typing import Any

from ...acquisition.evidence import ObservationAccounting
from ...acquisition.model import SourceAcquisition
from ...application.orchestration_errors import ApplicationError, ContractValidationError
from ...contracts.model import Artifact
from ...domain.diagnostics import Diagnostic, ValidationResult
from ...domain.evidence import ServiceHealthSupplementalEvidence
from ...domain.execution import ReportSelector, RunContext
from .article_text import plain_article, plain_text, recommended_action_section, text_retirement_claim
from .contract import SERVICE_HEALTH_V1
from ..model import PreparedRawReport, ReportDefinition

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
    if re.fullmatch(r"\d{4}(?:-\d{2})?", value):
        return "", "partial"
    try:
        return date.fromisoformat(value[:10]).isoformat(), "exact"
    except (TypeError, ValueError):
        return "", "invalid"

def _items(value: Any) -> tuple[Any, ...]:
    if isinstance(value, Mapping):
        return (value,) if value else ()
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return ()

def _impact_service_regions(
    properties: Mapping[str, Any],
) -> tuple[tuple[str, str, str], ...]:
    service_regions: list[tuple[str, str, str]] = []
    for impact in _items(properties.get("impact")):
        impact_map = _mapping(impact)
        impacted_service = impact_map.get("impactedService")
        impacted_service_map = _mapping(impacted_service)
        if impacted_service_map:
            service_name = str(
                impacted_service_map.get("serviceName")
                or impacted_service_map.get("name")
                or ""
            )
            service_guid = str(
                impacted_service_map.get("serviceGuid")
                or impacted_service_map.get("id")
                or impact_map.get("impactedServiceGuid")
                or ""
            )
        else:
            service_name = str(impacted_service or impact_map.get("serviceName") or "")
            service_guid = str(impact_map.get("impactedServiceGuid") or "")
        for region in _items(impact_map.get("impactedRegions")):
            region_map = _mapping(region)
            region_name = str(
                region_map.get("impactedRegion")
                or region_map.get("regionName")
                or region_map.get("name")
                or region_map.get("location")
                or (region if isinstance(region, str) else "")
            )
            if service_name and region_name:
                service_regions.append((service_name, service_guid, region_name))
    if service_regions:
        return tuple(dict.fromkeys(service_regions))
    for service in _items(properties.get("impactedServices")):
        service_map = _mapping(service)
        service_name = str(service_map.get("serviceName") or "")
        service_guid = str(service_map.get("serviceGuid") or "")
        for region in _items(service_map.get("impactedRegions")):
            region_map = _mapping(region)
            region_name = str(
                region_map.get("regionName")
                or region_map.get("regionId")
                or region_map.get("name")
                or region_map.get("location")
                or (region if isinstance(region, str) else "")
            )
            if service_name and region_name:
                service_regions.append((service_name, service_guid, region_name))
    return tuple(dict.fromkeys(service_regions))

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
    return _mapping(getattr(record, "payload", record))

def _collection_subscription(record: Any, event: Mapping[str, Any]) -> str:
    return str(
        event.get("subscriptionId")
        or event.get("subscription_id")
        or getattr(record, "subscription_id", "")
        or ""
    )

def _inventory_lookup(
    inventory: Mapping[str, Mapping[str, Any]] | tuple[object, ...], key: str
) -> tuple[Mapping[str, Any], bool]:
    if not isinstance(inventory, Mapping):
        return {}, False
    value = inventory.get(key) or inventory.get(key.casefold())
    if isinstance(value, Mapping):
        return value, False
    if isinstance(value, (tuple, list)):
        matches = tuple(item for item in value if isinstance(item, Mapping))
        if len(matches) == 1:
            return matches[0], False
        if len(matches) > 1:
            return {}, True
    return {}, False

def normalize_service_health(
    acquisition: SourceAcquisition,
    context: RunContext,
    evidence: ServiceHealthSupplementalEvidence,
) -> ValidationResult[Artifact[Mapping[str, str]]]:
    rows: list[dict[str, str]] = []
    companions: list[dict[str, Any]] = []
    accounting: list[dict[str, Any]] = []
    diagnostics: list[Diagnostic] = []
    for index, raw_record in enumerate(acquisition.records, start=1):
        event = _payload(raw_record)
        props = _mapping(event.get("properties"))
        source_identity = str(
            getattr(raw_record, "identity", "") or event.get("id") or f"record-{index}"
        )
        source_subscription = str(
            getattr(raw_record, "subscription_id", "")
            or event.get("subscriptionId")
            or event.get("subscription_id")
            or ""
        )
        event_id = str(event.get("id") or "")
        if not event_id:
            accounting.append(
                {
                    "source": "service-health",
                    "subscription_id": source_subscription,
                    "source_identity": source_identity,
                    "destination": "invalid",
                    "reason": "missing_service_health_event_id",
                }
            )
            diagnostics.append(
                Diagnostic(
                    "error",
                    "missing_service_health_event_id",
                    "normalization",
                    "service-health",
                    context.run_id,
                )
            )
            continue
        event_name = str(event.get("name") or "")
        event_type = str(props.get("eventType") or "")
        if event_type.casefold() != "healthadvisory":
            accounting.append(
                {
                    "source": "service-health",
                    "subscription_id": source_subscription,
                    "source_identity": source_identity,
                    "destination": "excluded",
                    "reason": f"event_type:{event_type.casefold() or 'missing'}",
                }
            )
            continue
        level = str(props.get("level") or "")
        status = str(props.get("status") or "")
        classification_valid = (
            event_type.casefold() == "healthadvisory"
            and level.casefold() in {"informational", "warning", "critical"}
            and status.casefold() in {"active", "resolved"}
        )
        if not classification_valid:
            accounting.append(
                {
                    "source": "service-health",
                    "subscription_id": source_subscription,
                    "source_identity": source_identity,
                    "destination": "invalid",
                    "reason": "invalid_service_health_classification",
                }
            )
            diagnostics.append(
                Diagnostic(
                    "error",
                    "invalid_service_health_classification",
                    "normalization",
                    "service-health",
                    context.run_id,
                    record_ref=event_id,
                )
            )
            continue
        tracking = str(props.get("trackingId") or event_name)
        if not tracking:
            accounting.append(
                {
                    "source": "service-health",
                    "subscription_id": source_subscription,
                    "source_identity": source_identity,
                    "destination": "invalid",
                    "reason": "missing_tracking_id",
                }
            )
            diagnostics.append(
                Diagnostic(
                    "error",
                    "missing_tracking_id",
                    "normalization",
                    "service-health",
                    context.run_id,
                    record_ref=event_id,
                )
            )
            continue
        if (
            props.get("trackingId")
            and event_name
            and str(props.get("trackingId")).casefold() != event_name.casefold()
        ):
            diagnostics.append(
                Diagnostic(
                    "error",
                    "tracking_id_mismatch",
                    "normalization",
                    "service-health",
                    context.run_id,
                    record_ref=event_id,
                )
            )
            continue
        article = _mapping(props.get("article"))
        raw_article = (
            article.get("articleContent")
            or props.get("description")
            or props.get("summary")
        )
        description = plain_article(raw_article)
        sensitive = (
            props.get("isSensitive") is True
            or str(props.get("isSensitive") or "").casefold() == "true"
        )
        description_quality = (
            "sensitive_unavailable"
            if sensitive and not raw_article
            else "full_article"
            if article.get("articleContent")
            else "description_fallback"
            if props.get("description")
            else "summary_fallback"
            if props.get("summary")
            else "missing"
        )
        description_source = (
            "properties.article.articleContent"
            if article.get("articleContent")
            else "properties.description"
            if props.get("description")
            else "properties.summary"
            if props.get("summary")
            else ""
        )
        native_actions = plain_text(props.get("recommendedActions"))
        article_actions = recommended_action_section(article.get("articleContent"))
        description_actions = (
            ""
            if article_actions
            else recommended_action_section(props.get("description"))
        )
        recommended_actions = native_actions or article_actions or description_actions
        recommended_actions_source = (
            "properties.recommendedActions"
            if native_actions
            else "properties.article.articleContent.Recommended action"
            if article_actions
            else "properties.description.Recommended action"
            if description_actions
            else ""
        )
        start, start_flag = _timestamp(props.get("impactStartTime"))
        mitigation, mitigation_flag = _timestamp(props.get("impactMitigationTime"))
        last_update, update_flag = _timestamp(props.get("lastUpdateTime"))
        retirement_raw = str(
            props.get("retirementDate") or props.get("retirement_date") or ""
        )
        retirement_date_source = (
            "properties.retirementDate"
            if props.get("retirementDate")
            else "properties.retirement_date"
            if props.get("retirement_date")
            else ""
        )
        text_retirement_raw, text_retirement_source = text_retirement_claim(
            props, article
        )
        if text_retirement_raw:
            if retirement_raw and retirement_raw[:10] != text_retirement_raw:
                retirement_raw = f"conflict:{retirement_raw},{text_retirement_raw}"
                sources = {retirement_date_source, text_retirement_source} - {""}
                retirement_date_source = "conflicting:" + ",".join(sorted(sources))
            elif not retirement_raw:
                retirement_raw = text_retirement_raw
                retirement_date_source = text_retirement_source
        retirement_date, retirement_quality = _date(retirement_raw)
        if retirement_raw.startswith("conflict:"):
            retirement_date = ""
            retirement_quality = "conflict"
        if not retirement_raw:
            retirement_quality = "unknown"
        event_flags = set(filter(None, (start_flag, mitigation_flag, update_flag)))
        if description_quality == "missing":
            event_flags.add("missing_description")
        if description_quality == "sensitive_unavailable":
            event_flags.add("sensitive_description_unavailable")
        if retirement_quality == "missing":
            event_flags.add("missing_retirement_date")
        if retirement_quality == "invalid":
            event_flags.add("invalid_retirement_date")
        if retirement_quality == "conflict":
            event_flags.add("conflicting_retirement_date")
        if recommended_actions and not native_actions:
            event_flags.add("action_from_text")
        event_flags = frozenset(event_flags)
        service_regions = list(_impact_service_regions(props))
        collection_subscription = _collection_subscription(raw_record, event)
        resources = _items(props.get("impactedResources"))
        associations: list[
            tuple[str, str, str, str, str, str, Mapping[str, Any] | None]
        ] = []
        if resources:
            for resource in resources:
                resource_map = _mapping(resource)
                associations.append(
                    (
                        str(resource_map.get("serviceName") or ""),
                        str(resource_map.get("serviceGuid") or ""),
                        str(
                            resource_map.get("regionName")
                            or resource_map.get("regionId")
                            or ""
                        ),
                        str(
                            resource_map.get("subscriptionId")
                            or resource_map.get("subscription_id")
                            or ""
                        ),
                        str(
                            resource_map.get("resourceId")
                            or resource_map.get("id")
                            or ""
                        ),
                        "service_health_resource",
                        None,
                    )
                )
        resource_graph_key = (tracking.casefold(), collection_subscription.casefold())
        resource_graph_associations: list[
            tuple[str, str, str, str, str, str, Mapping[str, Any] | None]
        ] = []
        for resource in evidence.resource_associations.get(resource_graph_key, ()):
            resource_map = _mapping(resource)
            resource_id = str(
                resource_map.get("resourceId") or resource_map.get("id") or ""
            )
            if not resource_id:
                continue
            resource_graph_associations.append(
                (
                    str(resource_map.get("serviceName") or ""),
                    str(resource_map.get("serviceGuid") or ""),
                    str(
                        resource_map.get("region")
                        or resource_map.get("targetRegion")
                        or ""
                    ),
                    str(resource_map.get("subscriptionId") or collection_subscription),
                    resource_id,
                    "service_health_resource_graph",
                    None,
                )
            )
        if not resources:
            associations = resource_graph_associations or [
                (*association, "", "", "none", None) for association in service_regions
            ]
        if not associations:
            associations = [("", "", "", "", "", "none", None)]
        for advisor_record in evidence.advisor_records:
            advisor_map = _mapping(advisor_record)
            advisor_tracking = str(
                advisor_map.get("tracking_id") or advisor_map.get("trackingId") or ""
            )
            if advisor_tracking and advisor_tracking.casefold() not in {
                tracking.casefold(),
                event_id.casefold(),
            }:
                continue
            advisor_resource = str(
                advisor_map.get("resource_id") or advisor_map.get("resourceId") or ""
            )
            advisor_subscription = str(
                advisor_map.get("subscription_id")
                or advisor_map.get("subscriptionId")
                or ""
            )
            if not advisor_resource and not advisor_subscription:
                continue
            if any(
                item[3] == advisor_subscription and item[4] == advisor_resource
                for item in associations
            ):
                continue
            associations.append(
                (
                    "",
                    "",
                    "",
                    advisor_subscription,
                    advisor_resource,
                    "advisor_recommendation",
                    advisor_map,
                )
            )
        source_row_start = len(rows)
        for (
            service_name,
            service_guid,
            region,
            affected_subscription,
            resource_id,
            resource_source,
            advisor_record,
        ) in associations:
            row_flags = set(event_flags)
            is_global = (
                props.get("isGlobal") is True
                or str(props.get("isGlobal") or "").casefold() == "true"
            )
            is_global = is_global and resource_source != "advisor_recommendation"
            subscription_id = (
                "" if is_global else affected_subscription or collection_subscription
            )
            if not subscription_id and not is_global:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "missing_affected_subscription",
                        "normalization",
                        "service-health",
                        context.run_id,
                        record_ref=event_id,
                    )
                )
                continue
            normalized_resource = (
                re.sub(r"/+", "/", resource_id.strip()).casefold().rstrip("/")
                if resource_id
                else ""
            )
            record_type = (
                "service_health_event_global"
                if is_global and not subscription_id and not resource_id
                else "service_health_event_resource"
                if resource_id
                else "service_health_event_service_region"
                if service_name or region
                else "service_health_event_subscription"
            )
            if resource_source == "advisor_recommendation":
                row_flags.add("subscription_association_supplemented")
            if not resource_id:
                row_flags.add("resource_not_published")
            resource_inventory, resource_ambiguous = _inventory_lookup(
                evidence.resource_inventory, normalized_resource
            )
            subscription_inventory, subscription_ambiguous = _inventory_lookup(
                evidence.subscription_inventory, subscription_id
            )
            if resource_ambiguous:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "ambiguous_resource_enrichment",
                        "normalization",
                        "service-health",
                        context.run_id,
                        record_ref=event_id,
                    )
                )
            if subscription_ambiguous:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "ambiguous_subscription_enrichment",
                        "normalization",
                        "service-health",
                        context.run_id,
                        record_ref=event_id,
                    )
                )
            if resource_id and not resource_inventory:
                row_flags.add("resource_inventory_not_found")
            if subscription_id and not subscription_inventory:
                row_flags.add("subscription_inventory_not_found")
            resource_status = (
                "not_applicable"
                if not resource_id
                else "matched"
                if resource_inventory
                else "missing"
            )
            subscription_status = (
                "not_applicable"
                if not subscription_id
                else "matched"
                if subscription_inventory
                else "missing"
            )
            resource_graph_queries = []
            if evidence.subscription_inventory or evidence.subscription_name_sources:
                resource_graph_queries.extend(
                    ("subscription_inventory", "service_health_impacted_resources")
                )
            if resource_id and resource_source == "service_health_resource_graph":
                resource_graph_queries.append("resource_inventory")
            ref = sha256(
                f"{context.run_id}\0{event_id}\0{subscription_id}\0{resource_id}\0{service_name}\0{region}".encode()
            ).hexdigest()
            row: dict[str, str] = {column: "" for column in SERVICE_HEALTH_V1.header}
            row.update(
                {
                    "schema_version": "1",
                    "run_id": context.run_id,
                    "as_of_date": context.as_of_date.isoformat(),
                    "scope_mode": context.scope.mode,
                    "record_type": record_type,
                    "source_system": "azure_service_health",
                    "service_health_event_id": event_id,
                    "event_name": event_name,
                    "tracking_id": tracking,
                    "collection_subscription_id": collection_subscription,
                    "subscription_id": subscription_id,
                    "subscription_name": str(subscription_inventory.get("name") or ""),
                    "subscription_evidence_source": "explicit_global"
                    if is_global and not subscription_id
                    else "advisor_recommendation"
                    if resource_source == "advisor_recommendation"
                    else "resource_health_endpoint",
                    "event_type": event_type,
                    "event_sub_type": str(props.get("eventSubType") or ""),
                    "event_source": str(props.get("eventSource") or ""),
                    "event_level": level,
                    "status": status,
                    "title": plain_text(props.get("title")),
                    "summary": plain_text(props.get("summary")),
                    "description_problem": description,
                    "description_quality": description_quality,
                    "recommended_actions": recommended_actions,
                    "impact_start_time_raw": str(props.get("impactStartTime") or ""),
                    "impact_start_time": start,
                    "impact_mitigation_time_raw": str(
                        props.get("impactMitigationTime") or ""
                    ),
                    "impact_mitigation_time": mitigation,
                    "last_update_time_raw": str(props.get("lastUpdateTime") or ""),
                    "last_update_time": last_update,
                    "retirement_date_raw": retirement_raw,
                    "retirement_date": retirement_date,
                    "retirement_date_source": retirement_date_source,
                    "retirement_date_quality": retirement_quality,
                    "impacted_service": service_name,
                    "impacted_service_guid": service_guid,
                    "impacted_region": region,
                    "normalized_impacted_region": "global"
                    if is_global
                    else region.casefold(),
                    "resource_evidence_source": resource_source,
                    "resource_evidence_status": "inventory_missing"
                    if resource_id and not resource_inventory
                    else "published"
                    if resource_id
                    else "not_published",
                    "published_resource_id": resource_id,
                    "normalized_resource_id": normalized_resource,
                    "resource_name": str(resource_inventory.get("name") or ""),
                    "resource_group": str(
                        resource_inventory.get("resourceGroup")
                        or resource_inventory.get("resource_group")
                        or ""
                    ),
                    "resource_type": str(
                        resource_inventory.get("type")
                        or resource_inventory.get("resourceType")
                        or ""
                    ),
                    "resource_location": str(resource_inventory.get("location") or ""),
                    "recommendation_type_id": str(
                        (advisor_record or {}).get("recommendation_type_id")
                        or (advisor_record or {}).get("recommendationTypeId")
                        or props.get("recommendationTypeId")
                        or ""
                    ),
                    "advisor_platform_state": str(
                        (advisor_record or {}).get("platform_state")
                        or (advisor_record or {}).get("platformState")
                        or ""
                    ),
                    "current_query_match": str(
                        (advisor_record or {}).get("current_query_match")
                        or (advisor_record or {}).get("currentQueryMatch")
                        or ""
                    ),
                    "resource_inventory_match_status": resource_status,
                    "subscription_inventory_match_status": subscription_status,
                    "is_sensitive": "true" if sensitive else "false",
                    "details_fetch_status": "unavailable_sensitive"
                    if sensitive and not raw_article
                    else "not_needed",
                    "diagnostic_flags": ",".join(sorted(row_flags)),
                    "provenance_json": _canonical(
                        {
                            "api_version": acquisition.receipt.api_version,
                            "event_id": event_id,
                            "association": record_type,
                            "subscription_name_source": evidence.subscription_name_sources.get(
                                subscription_id.casefold(), ""
                            ),
                            "resource_evidence_source": resource_source
                            if resource_id
                            else "not_published",
                            "resource_graph_queries": resource_graph_queries,
                            "field_sources": {
                                "description_problem": description_source,
                                "recommended_actions": recommended_actions_source,
                                "retirement_date": retirement_date_source,
                            },
                        }
                    ),
                    "raw_record_ref": ref,
                }
            )
            rows.append(row)
            companions.append(
                {
                    "schema_version": 1,
                    "run_id": context.run_id,
                    "raw_record_ref": ref,
                    "service_health_event": event,
                    "collection_subscription_id": collection_subscription,
                    "affected_subscription_id": subscription_id,
                    "service_health_resource_evidence": {"resourceId": resource_id}
                    if resource_id and resource_source == "service_health_resource"
                    else None,
                    "advisor_evidence": advisor_record,
                    "resource_inventory": resource_inventory or None,
                    "subscription_inventory": subscription_inventory or None,
                }
            )
        accounting.append(
            {
                "source": "service-health",
                "subscription_id": source_subscription,
                "source_identity": source_identity,
                "destination": "normalized"
                if len(rows) > source_row_start
                else "invalid",
                "reason": "health_advisory",
                "fanout_count": len(rows) - source_row_start,
            }
        )
    if diagnostics:
        return ValidationResult.invalid(tuple(diagnostics))
    for item in accounting:
        if "raw_payload" not in item:
            item["raw_payload"] = next(
                (
                    _payload(record)
                    for record in acquisition.records
                    if str(
                        getattr(record, "identity", "")
                        or _payload(record).get("id")
                        or ""
                    )
                    == item["source_identity"]
                ),
                {},
            )
    rows.sort(
        key=lambda row: (
            row["collection_subscription_id"].casefold(),
            row["service_health_event_id"].casefold(),
            row["subscription_id"].casefold(),
            row["record_type"],
            row["normalized_resource_id"].casefold(),
            row["impacted_service"].casefold(),
            row["normalized_impacted_region"],
            row["resource_evidence_source"],
        )
    )
    companion_by_ref = {item["raw_record_ref"]: item for item in companions}
    artifact = Artifact(
        "service-health",
        1,
        context.run_id,
        tuple(rows),
        tuple(companion_by_ref[row["raw_record_ref"]] for row in rows),
        tuple(accounting),
    )
    return ValidationResult.valid(artifact)

SERVICE_HEALTH_REPORT = ReportDefinition(
    selector=ReportSelector.SERVICE_HEALTH,
    name="service-health",
    stage="service-health",
    dependencies=(),
    contract=SERVICE_HEALTH_V1,
)

def prepare_service_health_report(
    acquisition: SourceAcquisition,
    context: RunContext,
    supplemental: ServiceHealthSupplementalEvidence = ServiceHealthSupplementalEvidence(),
) -> PreparedRawReport:
    if not acquisition.receipt.is_complete:
        failed = (
            acquisition.receipt.failed_subscriptions[0]
            if acquisition.receipt.failed_subscriptions
            else ""
        )
        if not failed:
            failed = (
                context.scope.subscription_ids[0]
                if context.scope.subscription_ids
                else ""
            )
        if not failed and acquisition.records:
            failed = str(getattr(acquisition.records[0], "subscription_id", ""))
        raise ApplicationError(
            "incomplete service-health acquisition",
            (
                Diagnostic(
                    "error",
                    "incomplete_acquisition",
                    "acquisition",
                    "service-health",
                    context.run_id,
                    message=f"incomplete acquisition for subscription: {failed}",
                ),
            ),
        )
    if not acquisition.records:
        if acquisition.receipt.source_records != 0:
            raise ApplicationError("inconsistent service-health acquisition receipt")
        artifact = SERVICE_HEALTH_V1.empty_artifact(context)
        normalized = acquisition
    else:
        result = normalize_service_health(acquisition, context, supplemental)
        if not result.is_valid or result.value is None:
            raise ContractValidationError(
                result.diagnostics, "invalid service-health raw contract"
            )
        artifact = result.value
        checked = SERVICE_HEALTH_V1.validate(artifact, context)
        if not checked.is_valid:
            raise ContractValidationError(
                checked.diagnostics, "invalid service-health raw contract"
            )
        normalized = SourceAcquisition(
            receipt=acquisition.receipt,
            records=artifact.records,
            companion_records=artifact.companion_records,
            accounting=tuple(
                ObservationAccounting(
                    source=item["source"],
                    subscription_id=item["subscription_id"],
                    source_identity=item["source_identity"],
                    destination=item["destination"],
                    reason=item.get("reason", ""),
                    raw_record_ref=item.get("raw_record_ref", ""),
                )
                for item in artifact.accounting
            ),
            collection_context=acquisition.collection_context,
            response_context=acquisition.response_context,
        )
    exported_records = []
    for row in artifact.records:
        value = dict(row)
        try:
            provenance = json.loads(value.get("provenance_json", "{}"))
        except json.JSONDecodeError:
            provenance = {}
        if isinstance(provenance, dict):
            provenance.pop("field_sources", None)
            value["provenance_json"] = _canonical(provenance)
        exported_records.append(value)
    export_artifact = Artifact(
        contract=artifact.contract,
        schema_version=artifact.schema_version,
        run_id=artifact.run_id,
        records=tuple(exported_records),
        companion_records=artifact.companion_records,
        accounting=artifact.accounting,
    )
    return PreparedRawReport(
        acquisition=normalized,
        artifact=artifact,
        artifacts=(
            SERVICE_HEALTH_V1.encode(export_artifact),
            SERVICE_HEALTH_V1.encode_companion(artifact),
        ),
    )

__all__ = ["SERVICE_HEALTH_REPORT", "normalize_service_health", "prepare_service_health_report"]
