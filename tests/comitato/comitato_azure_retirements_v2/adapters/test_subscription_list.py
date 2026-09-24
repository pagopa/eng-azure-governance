from datetime import date, datetime, timezone

from src.comitato.comitato_azure_retirements_v2.adapters.arm_http import ArmPageEnvelope
from src.comitato.comitato_azure_retirements_v2.adapters.subscription_list import (
    acquire_subscription_list,
)
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


class HttpWithTwoPages:
    def list_pages(self, url: str, **kwargs):
        return (
            ArmPageEnvelope(url, ({"id": "/items/1"},), "next"),
            ArmPageEnvelope("next", ({"id": "/items/2"},)),
        )


def _context() -> RunContext:
    request = RunRequest(ReportSelector.ALL, ("sub-a",), date(2026, 7, 31))
    return RunContext(
        run_id="run-1",
        as_of_date=date(2026, 7, 31),
        created_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
        request=request,
        scope=Scope(("sub-a",), mode="explicit"),
        catalog_identity=CatalogIdentity(1, "0" * 64),
        dependency_plan=DependencyPlan(("scope",)),
    )


def test_acquire_subscription_list_maps_complete_receipt() -> None:
    http = HttpWithTwoPages()

    acquisition = acquire_subscription_list(
        http,
        _context(),
        source="example",
        api_version="2026-01-01",
        response_name="Example",
        url_for=lambda subscription_id: (
            f"https://management.azure.com/{subscription_id}/items"
        ),
        params={"api-version": "2026-01-01"},
        annotate=lambda item, subscription_id: {
            **item,
            "subscriptionId": subscription_id,
        },
    )

    assert acquisition.receipt.source == "example"
    assert acquisition.receipt.expected_subscriptions == 1
    assert acquisition.receipt.pages == 2
    assert acquisition.receipt.is_complete
    assert acquisition.records[0].payload["subscriptionId"] == "sub-a"
