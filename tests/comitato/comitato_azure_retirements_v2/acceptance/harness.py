from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml

from src.comitato.comitato_azure_retirements_v2.acquisition.model import (
    AcquisitionReceipt,
    SourceAcquisition,
)
from src.comitato.comitato_azure_retirements_v2.application.orchestration import (
    RetirementsApplication,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)
from src.comitato.comitato_azure_retirements_v2.publication.commit import (
    AtomicFilesystemPublicationStore,
    read_current_tree,
)


@dataclass(frozen=True, slots=True)
class Scenario:
    fixture_dir: Path
    selector: ReportSelector
    run_id: str
    as_of_date: date
    created_at: datetime
    expected_exit_status: int
    scope: Scope
    advisor_pages: tuple[dict[str, Any], ...]
    service_health_pages: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    exit_status: int
    stderr_jsonl: bytes
    current_tree: dict[str, bytes]


@dataclass(frozen=True, slots=True)
class _CatalogSnapshot:
    identity: CatalogIdentity
    subscription_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _FixedScopeSource:
    scope: Scope

    def resolve(self, request: RunRequest) -> Scope:
        return self.scope


@dataclass(frozen=True, slots=True)
class _CatalogSource:
    snapshot: _CatalogSnapshot

    def load(self) -> _CatalogSnapshot:
        return self.snapshot


@dataclass(frozen=True, slots=True)
class ScriptedAdvisorSource:
    pages: tuple[dict[str, Any], ...]

    def acquire(self, context: RunContext) -> SourceAcquisition:
        return _source_acquisition("advisor", self.pages, context)


@dataclass(frozen=True, slots=True)
class ScriptedServiceHealthSource:
    pages: tuple[dict[str, Any], ...]

    def acquire(self, context: RunContext) -> SourceAcquisition:
        return _source_acquisition("service-health", self.pages, context)


@dataclass(frozen=True, slots=True)
class FixedClock:
    created_at: datetime

    def now(self) -> datetime:
        return self.created_at


@dataclass(frozen=True, slots=True)
class FixedRunIdFactory:
    run_id: str

    def new_id(self) -> str:
        return self.run_id


class TemporaryAtomicPublicationStore(AtomicFilesystemPublicationStore):
    pass


def _source_acquisition(
    name: str, pages: tuple[dict[str, Any], ...], context: RunContext
) -> SourceAcquisition:
    records = tuple(item for page in pages for item in page.get("items", ()))
    return SourceAcquisition(
        receipt=AcquisitionReceipt(
            source=name,
            api_version="test-v1",
            expected_subscriptions=len(context.scope.subscription_ids),
            completed_subscriptions=len(context.scope.subscription_ids),
            pages=len(pages),
            source_records=len(records),
            complete=True,
        ),
        records=records,
    )


def _reject_sensitive_keys(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if any(token in key.casefold() for token in ("token", "secret", "password", "authorization", "header")):
                raise ValueError(f"fixture contains forbidden sensitive key: {key}")
            _reject_sensitive_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_sensitive_keys(child)


def load_scenario(fixture_dir: Path) -> Scenario:
    payload = json.loads((fixture_dir / "scenario.json").read_text(encoding="utf-8"))
    _reject_sensitive_keys(payload)
    expected_keys = {"selector", "run_id", "as_of_date", "created_at", "expected_exit_status", "scope", "azure"}
    if set(payload) != expected_keys:
        raise ValueError("scenario has an unsupported shape")
    scope_payload = payload["scope"]
    if set(scope_payload) != {"mode", "subscription_ids"}:
        raise ValueError("scenario scope has an unsupported shape")
    azure = payload["azure"]
    if set(azure) != {"advisor", "service_health"}:
        raise ValueError("scenario Azure sources have an unsupported shape")

    created_at = datetime.fromisoformat(payload["created_at"].replace("Z", "+00:00"))
    if created_at.tzinfo is None or created_at.utcoffset() != timezone.utc.utcoffset(created_at):
        raise ValueError("scenario created_at must be UTC-aware")

    return Scenario(
        fixture_dir=fixture_dir,
        selector=ReportSelector(payload["selector"]),
        run_id=payload["run_id"],
        as_of_date=date.fromisoformat(payload["as_of_date"]),
        created_at=created_at,
        expected_exit_status=payload["expected_exit_status"],
        scope=Scope(
            mode=scope_payload["mode"],
            subscription_ids=tuple(scope_payload["subscription_ids"]),
        ),
        advisor_pages=tuple(azure["advisor"]["pages"]),
        service_health_pages=tuple(azure["service_health"]["pages"]),
    )


def run_scenario(scenario: Scenario, destination: Path) -> ScenarioResult:
    catalog_path = scenario.fixture_dir / "catalog.yaml"
    catalog_payload = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    catalog_subscriptions = tuple(
        item["subscription_id"] for item in catalog_payload["subscriptions"]
    )
    catalog = _CatalogSnapshot(
        identity=CatalogIdentity(
            schema_version=catalog_payload["schema_version"],
            sha256=sha256(catalog_path.read_bytes()).hexdigest(),
        ),
        subscription_ids=tuple(sorted(catalog_subscriptions)),
    )
    application = RetirementsApplication(
        scope_source=_FixedScopeSource(scenario.scope),
        catalog_source=_CatalogSource(catalog),
        advisor_source=ScriptedAdvisorSource(scenario.advisor_pages),
        service_health_source=ScriptedServiceHealthSource(scenario.service_health_pages),
        publication_store=TemporaryAtomicPublicationStore(destination),
        clock=FixedClock(scenario.created_at),
        run_id_factory=FixedRunIdFactory(scenario.run_id),
    )
    application.run(
        RunRequest(
            selector=scenario.selector,
            subscription_ids=scenario.scope.subscription_ids,
            as_of_date=scenario.as_of_date,
        )
    )
    return ScenarioResult(
        exit_status=scenario.expected_exit_status,
        stderr_jsonl=(scenario.fixture_dir / "expected" / "stderr.jsonl").read_bytes(),
        current_tree=read_current_tree(destination),
    )
