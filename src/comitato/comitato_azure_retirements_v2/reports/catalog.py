from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from ..contracts import AGGREGATE_V1, SLIDES_V1
from ..domain.diagnostics import Diagnostic, sort_diagnostics
from ..domain.execution import ReportSelector
from .advisor import ADVISOR_REPORT
from .model import ReportDefinition
from .service_health import SERVICE_HEALTH_REPORT


@dataclass(frozen=True, slots=True)
class EditorialItem:
    item_id: str
    associations: tuple[tuple[str, tuple[str, ...]], ...] = ()
    title: str = ""
    description: str = ""
    suggested_action: str = ""

    def source_identities(self, source: str) -> tuple[str, ...]:
        normalized = source.strip().casefold()
        for association_source, identities in self.associations:
            if association_source == normalized:
                return identities
        return ()


@dataclass(frozen=True, slots=True)
class EditorialCatalog:
    schema_version: int
    sha256: str
    items: tuple[EditorialItem, ...]

    @property
    def item_ids(self) -> tuple[str, ...]:
        return tuple(item.item_id for item in self.items)

    def item_for_source(self, source: str, identity: str) -> EditorialItem | None:
        source_key = source.strip().casefold()
        identity_key = identity.strip().casefold()
        for item in self.items:
            if identity_key in item.source_identities(source_key):
                return item
        return None

    def items_for_event(self, event: object) -> tuple[EditorialItem, ...]:
        source = str(getattr(event, "source", "")).strip().casefold()
        identities = {
            str(getattr(getattr(event, "key", None), "identity", "")).strip().casefold()
        }
        for row in getattr(event, "records", ()) or ():
            identities.update(_source_identities(source, row))
        return tuple(
            item for item in self.items
            if any(identity in item.source_identities(source) for identity in identities if identity)
        )

    def associations_for(self, item_id: str) -> tuple[tuple[str, str], ...]:
        for item in self.items:
            if item.item_id == item_id:
                return tuple((source, identity) for source, identities in item.associations for identity in identities)
        raise KeyError(item_id)

    def association_diagnostics(
        self,
        source_events: object,
        *,
        run_id: str = "",
        report: str = "aggregate",
    ) -> tuple[Diagnostic, ...]:
        rows = getattr(source_events, "records", source_events)
        if isinstance(rows, Mapping):
            rows = (rows,)
        ownership = {
            (source, identity): item.item_id
            for item in self.items
            for source, identities in item.associations
            for identity in identities
        }
        observed = set()
        diagnostics: list[Diagnostic] = []
        for event in rows or ():
            key = getattr(event, "key", None)
            source = str(getattr(key, "source", getattr(event, "source", ""))).strip().casefold()
            identity = str(getattr(key, "identity", "")).strip().casefold()
            event_identities = {identity} if identity else set()
            for row in getattr(event, "records", ()) or ():
                event_identities.update(_source_identities(source, row))
            matches = {
                ownership[(source, value)]
                for value in event_identities
                if (source, value) in ownership
            }
            observed.update((source, value) for value in event_identities)
            raw_refs = tuple(sorted({
                str(row.get("raw_record_ref", "")).strip()
                for row in getattr(event, "records", ()) or ()
                if str(row.get("raw_record_ref", "")).strip()
            }))
            event_ref = getattr(key, "value", "") or f"{source}:{identity}"
            if len(matches) > 1:
                diagnostics.append(Diagnostic(
                    "error",
                    "ambiguous_editorial_mapping",
                    "aggregate",
                    report,
                    run_id,
                    record_ref=event_ref,
                    message=f"source event maps to multiple editorial items; raw_record_refs={','.join(raw_refs)}",
                ))
            elif not matches:
                diagnostics.append(Diagnostic(
                    "warning",
                    "unassociated_editorial_source",
                    "aggregate",
                    report,
                    run_id,
                    record_ref=event_ref,
                    message=f"source event has no editorial item; raw_record_refs={','.join(raw_refs)}",
                ))
        for source, identity in sorted(set(ownership) - observed):
            diagnostics.append(Diagnostic(
                "warning",
                "unknown_editorial_association",
                "aggregate",
                report,
                run_id,
                record_ref=f"{source}:{identity}",
                message="editorial association was not present in the source events",
            ))
        return sort_diagnostics(diagnostics)


@dataclass(frozen=True, slots=True)
class EditorialWorkItem:
    item_id: str
    source_ids: tuple[str, ...]
    title: str
    description: str
    suggested_action: str
    review_reason: str
    source_fingerprint: str
    source_content: tuple[tuple[str, str], ...] = ()


def build_editorial_work_list(catalog: EditorialCatalog, source_events: object) -> tuple[EditorialWorkItem, ...]:
    """Return a deterministic, derived queue for editorial review."""

    rows = getattr(source_events, "records", source_events)
    if isinstance(rows, Mapping):
        rows = (rows,)
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for event in rows or ():
        key = getattr(event, "key", None)
        source = getattr(key, "source", "")
        identity = getattr(key, "identity", "")
        item = catalog.item_for_source(source, identity)
        if item is None:
            continue
        grouped.setdefault(item.item_id, []).extend(getattr(event, "records", ()) or (getattr(event, "row", {}),))
    result: list[EditorialWorkItem] = []
    for item in catalog.items:
        item_rows = grouped.get(item.item_id, [])
        fingerprint_payload = [_editorial_content(row) for row in item_rows]
        fingerprint = sha256(json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        source_content = tuple(sorted({
            (field, str(row.get(field, "")))
            for row in item_rows
            for field in ("problem", "description", "actions_json", "retirement_date", "retiring_feature", "impacted_service", "impacted_region", "learn_more_link", "source_link")
            if str(row.get(field, "")).strip()
        }))
        if not item_rows:
            review_reason = "unassociated_catalog_item"
        elif not item.title or not item.description or not item.suggested_action:
            review_reason = "missing_editorial_text"
        else:
            review_reason = "source_content_review"
        result.append(
            EditorialWorkItem(
                item_id=item.item_id,
                source_ids=tuple(sorted({str(row.get("raw_record_ref", "")) for row in item_rows if row.get("raw_record_ref")})),
                title=item.title,
                description=item.description,
                suggested_action=item.suggested_action,
                review_reason=review_reason,
                source_fingerprint=fingerprint,
                source_content=source_content,
            )
        )
    return tuple(result)


def _editorial_content(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "problem": _first_value(row, ("problem", "short_description_problem", "description_problem", "description")),
        "action": _first_value(row, ("action", "actions_json", "recommended_actions")),
        "version": _first_value(row, ("version", "retirement_version", "retiring_feature_version", "retiring_feature")),
        "deadline": {
            "value": _first_value(row, ("deadline", "retirement_date")),
            "quality": _first_value(row, ("retirement_date_quality",)),
        },
        "impact_scope": {
            "service": _first_value(row, ("impacted_service", "service_name")),
            "region": _first_value(row, ("impacted_region",)),
            "scope": _first_value(row, ("impact_scope", "subscription_evidence_source")),
            "global": _first_value(row, ("is_global",)),
        },
    }


def _first_value(row: Mapping[str, Any], fields: tuple[str, ...]) -> str:
    for field in fields:
        value = str(row.get(field, "")).strip()
        if value:
            return value
    return ""


def _source_identities(source: str, row: Mapping[str, Any]) -> set[str]:
    if source == "advisor":
        fields = ("recommendation_type_id", "advisor_recommendation_type_id", "advisor_recommendation_id")
    elif source == "service-health":
        fields = ("tracking_id", "service_health_tracking_id", "service_health_event_id")
    else:
        fields = ()
    return {
        str(row.get(field, "")).strip().casefold()
        for field in fields
        if str(row.get(field, "")).strip()
    }


class EditorialCatalogSource:
    """Read-only loader for the externally maintained editorial catalog."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> EditorialCatalog:
        try:
            raw = self.path.read_bytes()
        except OSError as exc:
            raise ValueError("editorial catalog is unreadable") from exc
        try:
            payload = yaml.safe_load(raw.decode("utf-8"))
        except (UnicodeError, yaml.YAMLError) as exc:
            raise ValueError("editorial catalog YAML is invalid") from exc
        if not isinstance(payload, Mapping) or payload.get("schema_version") != 1 or not isinstance(payload.get("items"), list):
            raise ValueError("editorial catalog shape is not schema version 1")

        items: list[EditorialItem] = []
        seen_item_ids: set[str] = set()
        ownership: dict[tuple[str, str], str] = {}
        for raw_item in payload["items"]:
            if not isinstance(raw_item, Mapping):
                raise ValueError("editorial catalog item shape is invalid")
            item_id = _required_text(raw_item.get("id"), "editorial item id")
            if item_id in seen_item_ids:
                raise ValueError("duplicate editorial item id")
            seen_item_ids.add(item_id)
            associations = _parse_associations(raw_item.get("associations", {}))
            for source, identities in associations:
                for identity in identities:
                    owner = ownership.setdefault((source, identity), item_id)
                    if owner != item_id:
                        raise ValueError("duplicate source ownership")
            items.append(
                EditorialItem(
                    item_id=item_id,
                    associations=associations,
                    title=_optional_text(raw_item.get("title")),
                    description=_optional_text(raw_item.get("description")),
                    suggested_action=_optional_text(raw_item.get("suggested_action")),
                )
            )
        return EditorialCatalog(1, sha256(raw).hexdigest(), tuple(sorted(items, key=lambda item: item.item_id)))


def _required_text(value: Any, label: str) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        raise ValueError(f"{label} is required")
    return text


def _optional_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _parse_associations(value: Any) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if not isinstance(value, Mapping):
        raise ValueError("editorial associations shape is invalid")
    field_names = {
        "advisor": ("recommendation_type_ids", "recommendation_ids"),
        "service_health": ("event_ids", "tracking_ids"),
        "service-health": ("event_ids", "tracking_ids"),
    }
    parsed: list[tuple[str, tuple[str, ...]]] = []
    for source, fields in field_names.items():
        if source not in value:
            continue
        source_value = value[source]
        if not isinstance(source_value, Mapping):
            raise ValueError("editorial source association shape is invalid")
        identities: set[str] = set()
        for field in fields:
            values = source_value.get(field, ())
            if isinstance(values, str):
                values = (values,)
            if not isinstance(values, (list, tuple)):
                raise ValueError("editorial source association values are invalid")
            identities.update(_required_text(item, "editorial source identity").casefold() for item in values)
        canonical_source = "service-health" if source == "service_health" else source
        if identities:
            parsed.append((canonical_source, tuple(sorted(identities))))
    return tuple(sorted(parsed))


@dataclass(frozen=True, slots=True)
class SelectedReportClosure:
    selector: ReportSelector
    stages: tuple[str, ...]
    required: tuple[ReportDefinition, ...]
    published: tuple[ReportDefinition, ...]
    path_owners: tuple[tuple[str, ReportDefinition], ...]

    def requires(self, selector: ReportSelector) -> bool:
        return any(item.selector is selector for item in self.required)

    def publishes(self, selector: ReportSelector) -> bool:
        return any(item.selector is selector for item in self.published)

    @property
    def expected_paths(self) -> tuple[str, ...]:
        return tuple(path for item in self.published for path in item.paths)

    @property
    def all_paths(self) -> tuple[str, ...]:
        return tuple(path for path, _ in self.path_owners)

    def owner_of(self, path: str) -> ReportDefinition:
        for owned_path, definition in self.path_owners:
            if owned_path == path:
                return definition
        raise KeyError(f"no report owns path: {path}")


class ReportCatalog:
    def __init__(self, definitions: tuple[ReportDefinition, ...]) -> None:
        selectors = tuple(item.selector for item in definitions)
        if len(selectors) != len(set(selectors)):
            raise ValueError("report selectors must be unique")
        paths = tuple(path for item in definitions for path in item.paths)
        if len(paths) != len(set(paths)):
            raise ValueError("report paths must be unique")
        self._definitions = definitions
        self._by_selector = {item.selector: item for item in definitions}
        self._by_path = {
            path: item for item in definitions for path in item.paths
        }

    @property
    def all_paths(self) -> tuple[str, ...]:
        return tuple(path for item in self._definitions for path in item.paths)

    def owner_of(self, path: str) -> ReportDefinition:
        try:
            return self._by_path[path]
        except KeyError as exc:
            raise KeyError(f"no report owns path: {path}") from exc

    def plan(self, selector: ReportSelector) -> SelectedReportClosure:
        roots = (
            self._definitions
            if selector is ReportSelector.ALL
            else (self._by_selector[selector],)
        )
        required: list[ReportDefinition] = []
        visited: set[ReportSelector] = set()

        def visit(current: ReportDefinition) -> None:
            if current.selector in visited:
                return
            for dependency in current.dependencies:
                visit(self._by_selector[dependency])
            visited.add(current.selector)
            required.append(current)

        for root in roots:
            visit(root)

        stages = ("scope", "catalog") + tuple(
            item.stage for item in required
        ) + ("publication",)
        published = tuple(
            item for item in roots if item.selector is not ReportSelector.ALL
        )
        if selector is ReportSelector.ALL:
            published = tuple(roots)
        path_owners = tuple(
            (path, definition)
            for definition in self._definitions
            for path in definition.paths
        )
        return SelectedReportClosure(
            selector,
            stages,
            tuple(required),
            published,
            path_owners,
        )


DEFAULT_REPORT_CATALOG = ReportCatalog(
    (
        ReportDefinition(
            ReportSelector.ADVISOR,
            "advisor",
            "advisor",
            (),
            ADVISOR_REPORT.contract,
        ),
        ReportDefinition(
            ReportSelector.SERVICE_HEALTH,
            "service-health",
            "service-health",
            (),
            SERVICE_HEALTH_REPORT.contract,
        ),
        ReportDefinition(
            ReportSelector.AGGREGATE,
            "aggregate",
            "aggregate",
            (ReportSelector.ADVISOR, ReportSelector.SERVICE_HEALTH),
            AGGREGATE_V1,
        ),
        ReportDefinition(
            ReportSelector.SLIDES,
            "slides",
            "slides",
            (ReportSelector.AGGREGATE,),
            SLIDES_V1,
        ),
    )
)


ReportPlan = SelectedReportClosure


__all__ = [
    "DEFAULT_REPORT_CATALOG",
    "EditorialCatalog",
    "EditorialCatalogSource",
    "EditorialItem",
    "EditorialWorkItem",
    "ReportCatalog",
    "ReportPlan",
    "SelectedReportClosure",
    "build_editorial_work_list",
]
