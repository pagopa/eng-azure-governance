from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from io import BytesIO
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from ..domain.diagnostics import Diagnostic, ValidationResult
from .model import Artifact, EncodedArtifact

HEADER = (
    "id_elemento",
    "titolo_breve",
    "descrizione_breve",
    "comitato_piattaforme",
    "comitato_priorità",
    "impatto_microsoft",
    "comitato_descrizione",
    "descrizione_originale_completa",
    "comitato_retirement_date",
    "retirement_date",
    "stato_data",
    "giorni_ritardo",
    "azione_originale",
    "fonti",
    "link_fonti",
    "ambito_impatto",
    "id_advisor",
    "id_service_health",
    "risorse_json",
)

ADVISOR_TYPE_LINK = "https://portal.azure.com/#view/Microsoft_Azure_Expert/RecommendationListBlade/recommendationTypeId/"
SERVICE_HEALTH_LINK = "https://app.azure.com/h/"
EXCEL_CELL_TEXT_LIMIT = 32_767

# (source, kind) -> (slide meaning, YAML tipo, YAML fonte)
DATE_KINDS = {
    ("advisor", "retirement"): (
        "Data di ritiro (Azure Advisor)",
        "ritiro",
        "Azure Advisor (raccomandazione)",
    ),
    ("advisor", "retirement_metadata"): (
        "Data di ritiro (metadati Azure Advisor)",
        "ritiro",
        "Azure Advisor (metadati)",
    ),
    ("advisor", "image_removal"): (
        "Rimozione immagine (Azure Advisor)",
        "rimozione_immagine",
        "Azure Advisor",
    ),
    ("advisor", "oldest_update"): (
        "Aggiornamento meno recente osservato (Azure Advisor)",
        "aggiornamento_meno_recente",
        "Azure Advisor",
    ),
    ("advisor", "last_updated"): (
        "Ultimo aggiornamento (Azure Advisor)",
        "ultimo_aggiornamento",
        "Azure Advisor",
    ),
    ("service-health", "retirement"): (
        "Data di ritiro (Azure Service Health)",
        "ritiro",
        "Azure Service Health",
    ),
    ("service-health", "oldest_update"): (
        "Aggiornamento meno recente osservato (Azure Service Health)",
        "aggiornamento_meno_recente",
        "Azure Service Health",
    ),
    ("service-health", "last_updated"): (
        "Ultimo aggiornamento (Azure Service Health)",
        "ultimo_aggiornamento",
        "Azure Service Health",
    ),
    ("service-health", "notice_start"): (
        "Avviso pubblicato il",
        "avviso_inizio",
        "Azure Service Health",
    ),
    ("service-health", "notice_end"): (
        "Avviso attivo fino al",
        "avviso_fine",
        "Azure Service Health",
    ),
}
_DATE_MEANINGS = {key: value[0] for key, value in DATE_KINDS.items()}
DATE_MEANING_TYPES = {
    meaning: (tipo, fonte) for meaning, tipo, fonte in DATE_KINDS.values()
}
_SOURCE_NAMES = {
    "advisor": "Azure Advisor",
    "azure-advisor": "Azure Advisor",
    "azure_advisor": "Azure Advisor",
    "service-health": "Azure Service Health",
    "azure-service-health": "Azure Service Health",
    "azure_service_health": "Azure Service Health",
}


def _json(row: Mapping[str, str], name: str, default: Any) -> Any:
    try:
        return json.loads(row.get(name, ""))
    except (TypeError, json.JSONDecodeError):
        return default


def _items(rows: tuple[Mapping[str, str], ...], column: str) -> list[Any]:
    values = []
    for row in rows:
        value = _json(row, column, [])
        if isinstance(value, list):
            values.extend(value)
    return values


def _unique(values: list[Any]) -> list[str]:
    rendered = set()
    for value in values:
        if isinstance(value, Mapping):
            value = next(
                (
                    value.get(field)
                    for field in (
                        "text",
                        "action",
                        "actionText",
                        "caption",
                        "label",
                        "description",
                        "title",
                        "name",
                    )
                    if value.get(field)
                ),
                json.dumps(
                    value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ),
            )
        text = str(value).strip()
        if text:
            rendered.add(text)
    return sorted(rendered, key=lambda item: (item.casefold(), item))


def _source_text(
    rows: tuple[Mapping[str, str], ...], fields: tuple[tuple[str, str], ...]
) -> str:
    sections = []
    for label, field in fields:
        values = _unique(_items(rows, field))
        if values:
            sections.append(f"{label}: {'\n\n'.join(values)}")
    return "\n\n".join(sections)


def _dates(rows: tuple[Mapping[str, str], ...]) -> list[dict[str, str]]:
    values = set()
    updates: dict[str, set[str]] = {}
    for row in rows:
        for item in _json(row, "date_events_json", []):
            if not isinstance(item, Mapping):
                continue
            date_value = str(item.get("date", "")).strip()
            source = str(item.get("source", "")).strip()
            kind = str(item.get("kind", "")).strip()
            if not date_value or (source, kind) not in _DATE_MEANINGS:
                continue
            if kind == "last_updated":
                updates.setdefault(source, set()).add(date_value)
            else:
                values.add((date_value, _DATE_MEANINGS[(source, kind)]))
    for source, update_dates in updates.items():
        values.add((max(update_dates), _DATE_MEANINGS[(source, "last_updated")]))
        if len(update_dates) > 1:
            values.add((min(update_dates), _DATE_MEANINGS[(source, "oldest_update")]))
    return [
        {"date": date_value, "meaning": meaning}
        for date_value, meaning in sorted(values)
    ]


def _resources(rows: tuple[Mapping[str, str], ...]) -> dict[str, Any]:
    if any(row.get("is_global") == "true" for row in rows):
        return {"ALL": "global"}
    resources: dict[str, dict[str, dict[str, set[str]]]] = {}
    for row in rows:
        platforms = _json(row, "platforms_subscriptions_json", {})
        provenance = _json(row, "provenance_json", {})
        evidence = (
            provenance.get("resource_evidence", [])
            if isinstance(provenance, Mapping)
            else []
        )
        names_by_subscription: dict[str, list[tuple[str, str]]] = {}
        for item in evidence if isinstance(evidence, list) else []:
            if isinstance(item, list | tuple) and len(item) == 5 and item[1]:
                names_by_subscription.setdefault(str(item[0]), []).append(
                    (str(item[2]) or "<unknown>", str(item[1]))
                )
        for platform, subscriptions in (
            platforms.items() if isinstance(platforms, Mapping) else ()
        ):
            for subscription in (
                subscriptions if isinstance(subscriptions, list) else ()
            ):
                if not isinstance(subscription, Mapping):
                    continue
                subscription_id = str(subscription.get("subscription_id", ""))
                subscription_name = str(subscription.get("subscription_name", ""))
                groups = resources.setdefault(str(platform), {}).setdefault(
                    subscription_name, {}
                )
                for group, name in names_by_subscription.get(subscription_id, []):
                    groups.setdefault(group, set()).add(name)
    return {
        platform: {
            subscription: {
                group: sorted(names, key=str.casefold)
                for group, names in sorted(
                    groups.items(), key=lambda pair: pair[0].casefold()
                )
            }
            for subscription, groups in sorted(
                subscriptions.items(), key=lambda pair: pair[0].casefold()
            )
        }
        for platform, subscriptions in sorted(
            resources.items(), key=lambda pair: pair[0].casefold()
        )
    }


def _impact_scope(rows: tuple[Mapping[str, str], ...]) -> dict[str, Any]:
    if any(row.get("is_global") == "true" for row in rows):
        return {"globale": True}
    platforms: dict[str, set[str]] = {}
    subscriptions: set[str] = set()
    environments = {"PROD": set(), "UAT": set(), "DEV": set(), "ALTRO": set()}
    services, regions = set(), set()
    resources: set[tuple[str, str, str]] = set()
    resource_platforms: dict[str, set[tuple[str, str, str]]] = {}
    for row in rows:
        services.update(_json(row, "impacted_services_json", []))
        regions.update(_json(row, "impacted_regions_json", []))
        provenance = _json(row, "provenance_json", {})
        evidence = (
            provenance.get("resource_evidence", [])
            if isinstance(provenance, Mapping)
            else []
        )
        evidence_rows = {
            (str(item[0]), str(item[2]) or "<unknown>", str(item[1]))
            for item in evidence
            if isinstance(item, list | tuple) and len(item) == 5 and item[1]
        }
        resources.update(evidence_rows)
        breakdown = _json(row, "platforms_subscriptions_json", {})
        for platform, entries in (
            breakdown.items() if isinstance(breakdown, Mapping) else ()
        ):
            platform = str(platform)
            platform_subscriptions = platforms.setdefault(platform, set())
            resource_platforms.setdefault(platform, set())
            for entry in entries if isinstance(entries, list) else ():
                if not isinstance(entry, Mapping):
                    continue
                sub_id = str(entry.get("subscription_id", ""))
                name = str(entry.get("subscription_name", ""))
                if sub_id:
                    subscriptions.add(sub_id)
                    platform_subscriptions.add(sub_id)
                match = re.match(r"^(PROD|UAT|DEV)[-_]", name, re.IGNORECASE)
                environments[match.group(1).upper() if match else "ALTRO"].add(
                    sub_id or name
                )
                resource_platforms[platform].update(
                    item for item in evidence_rows if item[0] == sub_id
                )
    return {
        "totale_piattaforme": len(platforms),
        "totale_subscription": len(subscriptions),
        "totale_risorse": len(resources),
        "ambienti": {key: len(value) for key, value in environments.items()},
        "servizi": sorted({str(value) for value in services}, key=str.casefold),
        "regioni": sorted({str(value) for value in regions}, key=str.casefold),
        "piattaforme": {
            platform: {
                "subscription": len(subscriptions_for_platform),
                "risorse": len(resource_platforms[platform]),
            }
            for platform, subscriptions_for_platform in sorted(
                platforms.items(), key=lambda pair: pair[0].casefold()
            )
        },
    }


@dataclass(frozen=True, slots=True)
class SlideRecord(Mapping[str, str]):
    values: tuple[tuple[str, str], ...]

    @classmethod
    def from_group(
        cls,
        rows: tuple[Mapping[str, str], ...],
        *,
        item_id: str,
        primary_date: str,
        status: str,
        days_overdue: str = "",
    ) -> "SlideRecord":
        titles = _unique(_items(rows, "problem_titles_json"))
        retiring = _unique([row.get("retiring_feature", "") for row in rows])
        services = _unique([row.get("technology_or_service", "") for row in rows])
        description = (titles or retiring or services or [""])[0]
        advisor_ids = _unique(_items(rows, "advisor_recommendation_type_ids_json"))
        health_ids = _unique(_items(rows, "service_health_tracking_ids_json"))
        impacts = {
            str(value).strip().casefold(): str(value).strip()
            for value in _items(rows, "advisor_impacts_json")
        }
        impact = next(
            (impacts[key] for key in ("high", "medium", "low") if key in impacts), ""
        )
        impact = {"High": "Alto", "Medium": "Medio", "Low": "Basso"}.get(impact, "")
        date_values = _dates(rows)
        date_cell = "\n".join(
            f"{item['date']} — {item['meaning']}" for item in date_values
        )
        source_values = _unique(_items(rows, "source_systems_json"))
        links = _unique(_items(rows, "source_links_json"))
        platforms = _unique(_items(rows, "platforms_json"))
        original_description = _source_text(
            rows,
            (
                ("Advisor", "advisor_problem_descriptions_json"),
                ("Service Health", "service_health_problem_descriptions_json"),
            ),
        )
        original_action = _source_text(
            rows,
            (
                ("Advisor", "advisor_actions_json"),
                ("Service Health", "service_health_actions_json"),
            ),
        )
        resource_value = json.dumps(
            _resources(rows), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        values = {
            "id_elemento": item_id,
            "titolo_breve": (services or retiring or description.splitlines() or [""])[
                0
            ],
            "descrizione_breve": description,
            "comitato_priorità": "",
            "impatto_microsoft": impact,
            "comitato_descrizione": "",
            "comitato_retirement_date": "",
            "comitato_piattaforme": "; ".join(platforms),
            "retirement_date": date_cell,
            "stato_data": status,
            "giorni_ritardo": days_overdue,
            "descrizione_originale_completa": original_description,
            "azione_originale": original_action,
            "fonti": "; ".join(
                _unique(
                    [
                        _SOURCE_NAMES.get(value.casefold(), value)
                        for value in source_values
                    ]
                )
            ),
            "link_fonti": "; ".join(links),
            "ambito_impatto": json.dumps(
                _impact_scope(rows),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
            "id_advisor": "; ".join(ADVISOR_TYPE_LINK + value for value in advisor_ids),
            "id_service_health": "; ".join(
                SERVICE_HEALTH_LINK + value for value in health_ids
            ),
            "risorse_json": resource_value,
        }
        return cls(tuple((column, values[column]) for column in HEADER))

    def __getitem__(self, key: str) -> str:
        return dict(self.values)[key]

    def __iter__(self) -> Iterator[str]:
        return (column for column, _ in self.values)

    def __len__(self) -> int:
        return len(self.values)


class SlidesV1Contract:
    name = "slides"
    header = HEADER
    path = "03_azure_retirements_slide.xlsx"
    companion_path = None
    schema_version = 1

    def empty_artifact(self, context) -> Artifact[SlideRecord]:
        return Artifact(
            contract=self.name,
            schema_version=self.schema_version,
            run_id=context.run_id,
        )

    def encode(self, artifact: Artifact[SlideRecord]) -> EncodedArtifact:
        workbook = Workbook()
        output = BytesIO()
        try:
            worksheet = workbook.active
            worksheet.title = "Azure Retirements"
            worksheet.append(self.header)
            for row_index, row in enumerate(artifact.records, start=2):
                for column_index, column in enumerate(self.header, start=1):
                    value = row[column]
                    if len(value) > EXCEL_CELL_TEXT_LIMIT:
                        raise ValueError(
                            f"slide cell {column} exceeds the Excel text limit "
                            f"of {EXCEL_CELL_TEXT_LIMIT} characters"
                        )
                    worksheet.cell(row_index, column_index, value).data_type = "s"
            workbook.save(output)
        finally:
            workbook.close()
        return EncodedArtifact(
            logical_path=self.path,
            data=output.getvalue(),
            rows=len(artifact.records),
            media_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
            schema_version=self.schema_version,
            run_id=artifact.run_id,
        )

    def decode(self, data: bytes) -> Artifact[Mapping[str, str]]:
        try:
            workbook = load_workbook(BytesIO(data), read_only=True, data_only=False)
        except (InvalidFileException, OSError, ValueError) as exc:
            raise ValueError("invalid slide workbook") from exc
        try:
            if len(workbook.worksheets) != 1:
                raise ValueError("slide workbook must contain one worksheet")
            rows = iter(workbook.active.iter_rows(values_only=True))
            header = tuple("" if value is None else str(value) for value in next(rows))
            if header != self.header:
                raise ValueError("invalid slide workbook header")
            records = tuple(
                dict(
                    zip(
                        self.header,
                        ("" if value is None else str(value) for value in row),
                        strict=True,
                    )
                )
                for row in rows
            )
        except StopIteration as exc:
            raise ValueError("invalid slide workbook header") from exc
        finally:
            workbook.close()
        return Artifact(
            contract=self.name,
            schema_version=self.schema_version,
            run_id="",
            records=records,
        )

    def validate(self, artifact, context):
        if (
            artifact.contract != self.name
            or artifact.schema_version != self.schema_version
        ):
            raise ValueError("artifact does not belong to this contract")
        if artifact.run_id != context.run_id:
            raise ValueError("artifact run_id does not match context")
        diagnostics: list[Diagnostic] = []
        seen: set[str] = set()
        for row in artifact.records:
            if tuple(row) != HEADER:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "invalid_slide_columns",
                        "validation",
                        "slides",
                        context.run_id,
                    )
                )
                continue
            if row["id_elemento"] in seen:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "duplicate_slide_id",
                        "validation",
                        "slides",
                        context.run_id,
                        record_ref=row["id_elemento"],
                    )
                )
            seen.add(row["id_elemento"])
            if row["comitato_priorità"]:
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "external_priority_required",
                        "validation",
                        "slides",
                        context.run_id,
                        record_ref=row["id_elemento"],
                    )
                )
        if diagnostics:
            return ValidationResult.invalid(tuple(diagnostics))
        return ValidationResult.valid(artifact)


SLIDES_V1 = SlidesV1Contract()


def encode(artifact):
    return SLIDES_V1.encode(artifact)


def decode(data: bytes):
    return SLIDES_V1.decode(data)


def validate(artifact, context):
    return SLIDES_V1.validate(artifact, context)


__all__ = ["HEADER", "SLIDES_V1", "SlideRecord", "decode", "encode", "validate"]
