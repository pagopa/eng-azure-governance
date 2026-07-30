"""Production composition root for the v2 modular monolith."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any, Mapping

from ..adapters.advisor_api import AdvisorApiSource
from ..adapters.arm_http import ArmHttpClient
from ..adapters.azure_auth import AzureCliTokenProvider
from ..adapters.filesystem_publication import FilesystemAtomicPublicationStore
from ..adapters.platform_catalog_yaml import YamlPlatformCatalogSource
from ..adapters.resource_health_api import ResourceHealthApiSource
from ..adapters.subscription_api import SubscriptionApiSource
from ..config import RuntimeConfig
from ..ports import Clock, RunIdFactory
from .orchestration import RetirementsApplication


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class UuidRunIdFactory:
    def new_id(self) -> str:
        return str(uuid4())


def build_application(
    config: RuntimeConfig,
    *,
    dependencies: Mapping[str, Any] | None = None,
) -> RetirementsApplication:
    overrides = dict(dependencies or {})
    http = overrides.get(
        "http",
        ArmHttpClient(
            AzureCliTokenProvider(),
            timeout_seconds=config.http.timeout_seconds,
            retry_attempts=config.http.retry_attempts,
            backoff_seconds=config.http.backoff_seconds,
        ),
    )
    return RetirementsApplication(
        scope_source=overrides.get("scope_source", SubscriptionApiSource(http)),
        catalog_source=overrides.get("catalog_source", YamlPlatformCatalogSource(config.catalog_path)),
        advisor_source=overrides.get("advisor_source", AdvisorApiSource(http, api_version=config.api_versions.advisor)),
        service_health_source=overrides.get("service_health_source", ResourceHealthApiSource(http, api_version=config.api_versions.resource_health)),
        publication_store=overrides.get("publication_store", FilesystemAtomicPublicationStore(config.output_path)),
        clock=overrides.get("clock", SystemClock()),
        run_id_factory=overrides.get("run_id_factory", UuidRunIdFactory()),
    )


__all__ = ["SystemClock", "UuidRunIdFactory", "build_application"]
