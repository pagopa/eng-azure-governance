from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
import json
import re
from datetime import timezone
from hashlib import sha256
from typing import Any

from ..acquisition.model import SourceAcquisition
from ..application.orchestration_errors import ApplicationError, ContractValidationError
from ..contracts._base import TsvContract
from ..contracts.model import Artifact
from ..domain.diagnostics import Diagnostic, ValidationResult
from ..domain.evidence import AdvisorEnrichments
from ..domain.execution import ReportSelector, RunContext
from .model import PreparedRawReport, ReportDefinition


HEADER = (
    "schema_version", "run_id", "as_of_date", "scope_mode", "record_type",
    "source_system", "advisor_recommendation_id", "recommendation_type_id",
    "recommendation_status", "subscription_id", "subscription_name",
    "resource_linkage_source", "published_resource_id", "normalized_resource_id",
    "resource_name", "resource_group", "resource_type", "location", "tags_json",
    "advisor_metadata_id", "service_name", "retiring_feature", "retirement_date_raw",
    "retirement_date", "retirement_date_source", "retirement_date_quality", "impact",
    "risk", "category", "sub_category", "last_updated", "label",
    "short_description_problem", "short_description_solution", "description",
    "potential_benefits", "learn_more_link", "actions_json", "metadata_match_status",
    "resource_inventory_match_status", "subscription_inventory_match_status",
    "diagnostic_flags", "provenance_json", "raw_record_ref",
)

ADVISOR_V1_HEADER = HEADER


class AdvisorV1Contract(TsvContract[Mapping[str, str]]):
    def validate(self, artifact, context):
        base = super().validate(artifact, context)
        diagnostics: list[Diagnostic] = []
        recommendation_ids: set[str] = set()
        refs: set[str] = set()
        row_refs: list[str] = []
        expected_keys = set(self.header)
        for row in artifact.records:
            if set(row) != expected_keys:
                diagnostics.append(Diagnostic("error", "invalid_advisor_columns", "validation", "advisor", context.run_id))
                continue
            recommendation_id = row.get("advisor_recommendation_id", "")
            ref = row.get("raw_record_ref", "")
            if not recommendation_id or recommendation_id in recommendation_ids:
                diagnostics.append(Diagnostic("error", "duplicate_or_missing_recommendation_id", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            recommendation_ids.add(recommendation_id)
            if not ref or ref in refs:
                diagnostics.append(Diagnostic("error", "duplicate_or_missing_raw_record_ref", "validation", "advisor", context.run_id, record_ref=ref))
            refs.add(ref)
            row_refs.append(ref)
            if row.get("run_id") != context.run_id or row.get("schema_version") != "1" or row.get("record_type") != "advisor_retirement_recommendation" or row.get("source_system") != "azure_advisor" or row.get("recommendation_status", "").casefold() != "new" or not row.get("subscription_id"):
                diagnostics.append(Diagnostic("error", "invalid_advisor_row", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            linkage = row.get("resource_linkage_source", "")
            if linkage not in {"resource_id", "legacy_id", "missing"}:
                diagnostics.append(Diagnostic("error", "invalid_resource_linkage_source", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            published = row.get("published_resource_id", "")
            normalized = re.sub(r"/+", "/", published.strip()).casefold().rstrip("/") if published else ""
            if normalized != row.get("normalized_resource_id", ""):
                diagnostics.append(Diagnostic("error", "resource_normalization_mismatch", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            if row.get("retirement_date_quality") not in {"exact", "missing", "invalid"}:
                diagnostics.append(Diagnostic("error", "invalid_retirement_date_quality", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            if row.get("retirement_date"):
                try:
                    date.fromisoformat(row["retirement_date"])
                except ValueError:
                    diagnostics.append(Diagnostic("error", "invalid_retirement_date", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            if row.get("last_updated"):
                try:
                    datetime.fromisoformat(row["last_updated"].replace("Z", "+00:00"))
                except ValueError:
                    diagnostics.append(Diagnostic("error", "invalid_last_updated", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            for field in ("tags_json", "actions_json", "provenance_json"):
                if row.get(field):
                    try:
                        json.loads(row[field])
                    except json.JSONDecodeError:
                        diagnostics.append(Diagnostic("error", f"invalid_{field}", "validation", "advisor", context.run_id, record_ref=recommendation_id))
            for field, allowed in {
                "metadata_match_status": {"matched", "missing", "ambiguous"},
                "resource_inventory_match_status": {"matched", "missing", "ambiguous"},
                "subscription_inventory_match_status": {"matched", "missing", "ambiguous"},
            }.items():
                if row.get(field) not in allowed:
                    diagnostics.append(Diagnostic("error", f"invalid_{field}", "validation", "advisor", context.run_id, record_ref=recommendation_id))
        companion_refs = tuple(str(item.get("raw_record_ref", "")) for item in artifact.companion_records if isinstance(item, Mapping))
        if len(companion_refs) != len(artifact.records) or tuple(row_refs) != companion_refs or len(set(companion_refs)) != len(companion_refs):
            diagnostics.append(Diagnostic("error", "raw_pair_bijection_failed", "validation", "advisor", context.run_id))
        for row, companion in zip(artifact.records, artifact.companion_records, strict=False):
            if not isinstance(companion, Mapping) or companion.get("raw_record_ref") != row.get("raw_record_ref") or companion.get("advisor_recommendation_id") != row.get("advisor_recommendation_id"):
                diagnostics.append(Diagnostic("error", "raw_evidence_not_reproducible", "validation", "advisor", context.run_id, record_ref=row.get("advisor_recommendation_id", "")))
        if diagnostics:
            return ValidationResult.invalid(tuple(diagnostics))
        return base


ADVISOR_V1 = AdvisorV1Contract(
    name="advisor",
    header=HEADER,
    path="01_azure_advisor_retirements_raw.tsv",
    companion_path="01_azure_advisor_retirements_raw.jsonl",
)


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


def _lookup(value: Mapping[str, Any], key: str) -> tuple[Mapping[str, Any] | None, bool]:
    folded_key = key.casefold()
    candidate = value.get(key)
    if candidate is None:
        for stored_key, stored_value in value.items():
            if str(stored_key).casefold() == folded_key:
                candidate = stored_value
                break
    if isinstance(candidate, Mapping):
        return candidate, False
    if isinstance(candidate, (tuple, list)):
        matches = tuple(item for item in candidate if isinstance(item, Mapping))
        if len(matches) == 1:
            return matches[0], False
        if len(matches) > 1:
            return None, True
    return None, False


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Mapping):
        for key in ("problem", "description", "text", "content"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()
    return ""


def _nested_mapping(value: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    candidate = value.get(key)
    return candidate if isinstance(candidate, Mapping) else {}


def _metadata_value(metadata: Mapping[str, Any], key: str) -> tuple[Any, str]:
    if key in metadata and metadata[key] not in (None, ""):
        return metadata[key], f"metadata.{key}"
    properties = _nested_mapping(metadata, "properties")
    if key in properties and properties[key] not in (None, ""):
        return properties[key], f"metadata.properties.{key}"
    return None, ""


def _metadata_resource_singular(metadata: Mapping[str, Any]) -> tuple[str, str]:
    resource_metadata, source = _metadata_value(metadata, "resourceMetadata")
    if isinstance(resource_metadata, Mapping):
        singular = _text(resource_metadata.get("singular"))
        if singular:
            return singular, f"{source}.singular"
    return "", ""


def _recommendation_value(
    recommendation: Mapping[str, Any],
    properties: Mapping[str, Any],
    key: str,
) -> tuple[Any, str]:
    for container, source in ((recommendation, f"advisor.{key}"), (properties, f"advisor.properties.{key}")):
        if key in container and container[key] not in (None, ""):
            return container[key], source
    return None, ""


RESOURCE_TYPE_LABELS = {
    "microsoft.cache/redis": "Redis Cache Server",
    "microsoft.cdn/profiles": "Front Door Profile",
    "microsoft.compute/disks": "Disk",
    "microsoft.compute/virtualmachines": "Virtual machine",
    "microsoft.containerregistry/registries": "Container registry",
    "microsoft.containerservice/managedclusters": "Kubernetes service",
    "microsoft.documentdb/databaseaccounts": "Cosmos DB account",
    "microsoft.insights/webtests": "Availability test",
    "microsoft.keyvault/vaults": "Key vault",
    "microsoft.network/applicationgateways": "Application gateway",
    "microsoft.network/publicipaddresses": "Public IP address",
    "microsoft.storage/storageaccounts": "Storage Account",
    "microsoft.web/sites": "App service",
}


def _fallback_service_name(resource_type: str) -> str:
    normalized = resource_type.strip().casefold()
    if normalized in RESOURCE_TYPE_LABELS:
        return RESOURCE_TYPE_LABELS[normalized]
    if normalized:
        provider = normalized.split("/", 1)[0].split(".", 1)[-1]
        return provider.replace("_", " ").title()
    return ""


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
        return "", "invalid_last_updated"


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
) -> ValidationResult[Artifact[Mapping[str, str]]]:
    rows: list[dict[str, str]] = []
    companions: list[dict[str, Any]] = []
    diagnostics: list[Diagnostic] = []
    for raw_record in acquisition.records:
        recommendation = _record_payload(raw_record)
        properties = _mapping(recommendation.get("properties"))
        recommendation_id = str(
            recommendation.get("id") or recommendation.get("advisorRecommendationId") or ""
        )
        if not recommendation_id:
            diagnostics.append(Diagnostic("error", "missing_recommendation_id", "normalization", "advisor", context.run_id))
            continue
        status_value = properties.get("recommendationStatus")
        status = "New" if "recommendationStatus" not in properties else str(status_value or "")
        if status.casefold() != "new":
            if not status or status.casefold() not in {"inprogress", "completed", "postponed", "dismissed"}:
                diagnostics.append(Diagnostic("error", "invalid_recommendation_status", "normalization", "advisor", context.run_id, record_ref=recommendation_id))
            continue
        subscription_id = _subscription_id(recommendation, recommendation_id)
        if not subscription_id:
            diagnostics.append(Diagnostic("error", "missing_subscription_id", "normalization", "advisor", context.run_id, record_ref=recommendation_id))
            continue
        metadata = _mapping(properties.get("resourceMetadata"))
        published = str(metadata.get("resourceId") or metadata.get("resource_id") or "")
        linkage = "resource_id"
        if not published:
            published = str(metadata.get("id") or "")
            linkage = "legacy_id" if published else "missing"
        normalized = _normalized_arm(published) if published else ""
        name, group, resource_type = _resource_parts(published)
        extended_properties = _mapping(properties.get("extendedProperties") or properties.get("extended_properties"))
        retirement_date_source = ""
        retirement_raw = properties.get("retirementDate") or properties.get("retirement_date")
        if retirement_raw:
            retirement_date_source = "properties.retirementDate" if properties.get("retirementDate") else "properties.retirement_date"
        else:
            retirement_raw = extended_properties.get("retirementDate") or extended_properties.get("retirement_date")
            if retirement_raw:
                retirement_date_source = "properties.extendedProperties.retirementDate" if extended_properties.get("retirementDate") else "properties.extendedProperties.retirement_date"
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
        recommendation_type_id = str(
            properties.get("recommendationTypeId")
            or recommendation.get("recommendationTypeId")
            or ""
        )
        short_description = _mapping(
            properties.get("shortDescription")
            or recommendation.get("shortDescription")
        )
        metadata_record: Mapping[str, Any] | None = None
        metadata_ambiguous = False
        metadata_key = ""
        if isinstance(enrichments.metadata, Mapping):
            for candidate in (
                recommendation_type_id,
                recommendation_id,
                f"{recommendation_type_id}\0{normalized}",
            ):
                if not candidate:
                    continue
                metadata_record, metadata_ambiguous = _lookup(enrichments.metadata, candidate)
                metadata_key = candidate
                if metadata_record is not None or metadata_ambiguous:
                    break
        resource_record, resource_ambiguous = (
            _lookup(enrichments.resources, normalized)
            if isinstance(enrichments.resources, Mapping)
            else (None, False)
        )
        subscription_key = subscription_id.casefold()
        subscription_record, subscription_ambiguous = (
            _lookup(enrichments.subscriptions, subscription_key)
            if isinstance(enrichments.subscriptions, Mapping)
            else (None, False)
        )
        if metadata_ambiguous:
            diagnostics.append(Diagnostic("error", "ambiguous_metadata_enrichment", "normalization", "advisor", context.run_id, record_ref=recommendation_id))
        if resource_ambiguous:
            diagnostics.append(Diagnostic("error", "ambiguous_resource_enrichment", "normalization", "advisor", context.run_id, record_ref=recommendation_id))
        if subscription_ambiguous:
            diagnostics.append(Diagnostic("error", "ambiguous_subscription_enrichment", "normalization", "advisor", context.run_id, record_ref=recommendation_id))
        metadata_record = metadata_record or {}
        resource_record = resource_record or {}
        subscription_record = subscription_record or {}
        direct_description, description_source = _recommendation_value(
            recommendation, properties, "description"
        )
        description = _text(direct_description)
        if not description:
            metadata_description, description_source = _metadata_value(
                metadata_record, "description"
            )
            description = _text(metadata_description)
        if not description:
            description = _text(short_description.get("problem"))
            description_source = "advisor.shortDescription.problem" if description else ""
        resource_name = str(resource_record.get("name") or name)
        resource_group = str(resource_record.get("resourceGroup") or resource_record.get("resource_group") or group)
        resource_type = str(resource_record.get("type") or resource_record.get("resourceType") or resource_type)
        location = str(resource_record.get("location") or "")
        tags = resource_record.get("tags") if isinstance(resource_record.get("tags"), Mapping) else {}
        metadata_id = str(metadata_record.get("id") or metadata_record.get("metadataId") or "")
        direct_service_name, service_name_source = _recommendation_value(
            recommendation, properties, "serviceName"
        )
        service_name = _text(direct_service_name)
        if not service_name:
            metadata_service_name, service_name_source = _metadata_value(
                metadata_record, "serviceName"
            )
            service_name = _text(metadata_service_name)
        if not service_name:
            service_name, service_name_source = _metadata_resource_singular(metadata_record)
        if not service_name:
            service_name = _fallback_service_name(resource_type)
            service_name_source = "resource.type.fallback" if service_name else ""
        retiring_feature = str(
            properties.get("retiringFeature")
            or properties.get("retiring_feature")
            or extended_properties.get("retirementFeatureName")
            or extended_properties.get("retirement_feature_name")
            or _metadata_value(metadata_record, "retiringFeature")[0]
            or _metadata_value(metadata_record, "retiring_feature")[0]
            or ""
        )
        subscription_name = _text(
            subscription_record.get("name")
            or subscription_record.get("subscriptionName")
        )
        metadata_status = "ambiguous" if metadata_ambiguous else "matched" if metadata_record else "missing"
        resource_status = "ambiguous" if resource_ambiguous else "matched" if resource_record else "missing"
        subscription_status = "ambiguous" if subscription_ambiguous else "matched" if subscription_record else "missing"
        if not description:
            flags.add("missing_description")
        if metadata_status == "missing":
            flags.add("metadata_not_found")
        if resource_status == "missing":
            flags.add("resource_inventory_not_found")
        if subscription_status == "missing":
            flags.add("subscription_inventory_not_found")
        direct_benefits, benefits_source = _recommendation_value(
            recommendation, properties, "potentialBenefits"
        )
        potential_benefits = _text(direct_benefits)
        if not potential_benefits:
            metadata_benefits, benefits_source = _metadata_value(
                metadata_record, "potentialBenefits"
            )
            potential_benefits = _text(metadata_benefits)
        direct_link, link_source = _recommendation_value(
            recommendation, properties, "learnMoreLink"
        )
        learn_more_link = _text(direct_link)
        if not learn_more_link:
            metadata_link, link_source = _metadata_value(metadata_record, "learnMoreLink")
            learn_more_link = _text(metadata_link)
        direct_label, label_source = _recommendation_value(
            recommendation, properties, "label"
        )
        label = _text(direct_label)
        if not label:
            metadata_label, label_source = _metadata_value(metadata_record, "label")
            label = _text(metadata_label)
        direct_actions, actions_source = _recommendation_value(
            recommendation, properties, "actions"
        )
        actions = direct_actions
        if actions is None or actions == "":
            actions, actions_source = _metadata_value(metadata_record, "actions")
        if actions is None or actions == "":
            actions = []
            actions_source = "default.empty"
        if not learn_more_link:
            flags.add("missing_learn_more_link")
        if not potential_benefits:
            flags.add("missing_potential_benefits")
        if not label:
            flags.add("missing_label")
        embedded_subscription = re.search(r"/subscriptions/([^/]+)", published, re.IGNORECASE)
        if embedded_subscription and embedded_subscription.group(1).casefold() != subscription_id.casefold():
            diagnostics.append(Diagnostic("error", "resource_subscription_mismatch", "normalization", "advisor", context.run_id, subscription_id=subscription_id, record_ref=recommendation_id))
        last_updated_raw = properties.get("lastUpdated") or properties.get("lastUpdatedTime")
        last_updated, last_updated_flag = _timestamp(last_updated_raw)
        if last_updated_flag:
            diagnostics.append(Diagnostic("error", last_updated_flag, "normalization", "advisor", context.run_id, record_ref=recommendation_id))
        ref = sha256(f"{context.run_id}\0{recommendation_id}".encode()).hexdigest()
        row: dict[str, str] = {column: "" for column in ADVISOR_V1.header}
        row.update(
            {
                "schema_version": "1", "run_id": context.run_id, "as_of_date": context.as_of_date.isoformat(), "scope_mode": context.scope.mode,
                "record_type": "advisor_retirement_recommendation", "source_system": "azure_advisor", "advisor_recommendation_id": recommendation_id,
                "recommendation_type_id": str(properties.get("recommendationTypeId") or ""), "recommendation_status": status, "subscription_id": subscription_id,
                "subscription_name": subscription_name, "resource_linkage_source": linkage, "published_resource_id": published, "normalized_resource_id": normalized,
                "resource_name": resource_name, "resource_group": resource_group, "resource_type": resource_type, "location": location, "tags_json": _canonical(tags),
                "advisor_metadata_id": metadata_id, "service_name": service_name, "retiring_feature": retiring_feature, "retirement_date_raw": str(retirement_raw or ""),
                "retirement_date": retirement_date, "retirement_date_source": retirement_date_source, "retirement_date_quality": retirement_quality,
                "impact": str(properties.get("impact") or ""), "risk": str(properties.get("risk") or ""), "category": str(properties.get("category") or ""),
                "sub_category": str(properties.get("subcategory") or properties.get("subCategory") or ""), "last_updated": last_updated, "label": label,
                "short_description_problem": _text(short_description.get("problem")), "short_description_solution": _text(short_description.get("solution")), "description": description,
                "potential_benefits": potential_benefits, "learn_more_link": learn_more_link, "actions_json": _canonical(actions),
                "metadata_match_status": metadata_status, "resource_inventory_match_status": resource_status, "subscription_inventory_match_status": subscription_status,
                "diagnostic_flags": ",".join(sorted(flags)), "provenance_json": _canonical({"recommendation_id": recommendation_id, "resource_linkage": linkage, "api_version": acquisition.receipt.api_version, "acquisition": "advisor.recommendations", "lookup_keys": {"metadata": metadata_key, "resource": normalized, "subscription": subscription_key}, "enrichment": {"metadata_key": metadata_key, "resource_key": normalized, "subscription_key": subscription_key}, "match_status": {"metadata": metadata_status, "resource": resource_status, "subscription": subscription_status}, "field_sources": {"service_name": service_name_source, "description": description_source, "potential_benefits": benefits_source, "learn_more_link": link_source, "label": label_source, "actions": actions_source}, "fields": {"resource_id": "properties.resourceMetadata.resourceId" if linkage == "resource_id" else "properties.resourceMetadata.id" if linkage == "legacy_id" else "", "description": description_source}}),
                "raw_record_ref": ref,
            }
        )
        rows.append(row)
        companions.append({"schema_version": 1, "run_id": context.run_id, "raw_record_ref": ref, "advisor_recommendation_id": recommendation_id, "recommendation": recommendation, "advisor_metadata": metadata_record or None, "resource_inventory": resource_record or None, "subscription_inventory": subscription_record or None})
    if diagnostics:
        return ValidationResult.invalid(tuple(diagnostics))
    ordered = tuple(sorted(rows, key=lambda row: (row["subscription_id"].casefold(), row["advisor_recommendation_id"].casefold(), row["normalized_resource_id"].casefold(), row["recommendation_type_id"].casefold())))
    by_ref = {item["raw_record_ref"]: item for item in companions}
    ordered_companions = tuple(by_ref[row["raw_record_ref"]] for row in ordered)
    artifact = Artifact("advisor", 1, context.run_id, ordered, ordered_companions)
    return ValidationResult.valid(artifact)


ADVISOR_REPORT = ReportDefinition(
    selector=ReportSelector.ADVISOR,
    name="advisor",
    stage="advisor",
    dependencies=(),
    contract=ADVISOR_V1,
)


def prepare_advisor_report(
    acquisition: SourceAcquisition,
    context: RunContext,
    enrichments: AdvisorEnrichments = AdvisorEnrichments(),
) -> PreparedRawReport:
    if not acquisition.receipt.is_complete:
        raise ApplicationError("incomplete advisor acquisition")
    if not acquisition.records:
        if acquisition.receipt.source_records != 0:
            raise ApplicationError("inconsistent advisor acquisition receipt")
        artifact = ADVISOR_V1.empty_artifact(context)
        normalized = acquisition
    else:
        result = normalize_advisor(acquisition, context, enrichments)
        if not result.is_valid or result.value is None:
            raise ContractValidationError(result.diagnostics, "invalid advisor raw contract")
        artifact = result.value
        checked = ADVISOR_V1.validate(artifact, context)
        if not checked.is_valid:
            raise ContractValidationError(checked.diagnostics, "invalid advisor raw contract")
        normalized = SourceAcquisition(
            receipt=acquisition.receipt,
            records=artifact.records,
            companion_records=artifact.companion_records,
        )
    return PreparedRawReport(
        acquisition=normalized,
        artifact=artifact,
        artifacts=(ADVISOR_V1.encode(artifact), ADVISOR_V1.encode_companion(artifact)),
    )


__all__ = [
    "ADVISOR_REPORT",
    "ADVISOR_V1",
    "ADVISOR_V1_HEADER",
    "AdvisorEnrichments",
    "AdvisorV1Contract",
    "HEADER",
    "normalize_advisor",
    "prepare_advisor_report",
]
