from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from src.comitato.comitato_azure_retirements_v2.adapters.advisor_api import AdvisorApiSource
from src.comitato.comitato_azure_retirements_v2.adapters.resource_graph_api import ResourceGraphApiSource
from src.comitato.comitato_azure_retirements_v2.adapters.resource_health_api import ResourceHealthApiSource
from src.comitato.comitato_azure_retirements_v2.adapters.subscription_api import SubscriptionApiSource
from src.comitato.comitato_azure_retirements_v2.adapters.arm_http import ArmPageEnvelope
from src.comitato.comitato_azure_retirements_v2.domain.execution import (
    CatalogIdentity,
    DependencyPlan,
    ReportSelector,
    RunContext,
    RunRequest,
    Scope,
)


class Http:
    def __init__(self):
        self.list_calls = []
        self.post_calls = []

    def list_pages(self, url, **kwargs):
        self.list_calls.append((url, kwargs))
        if "Microsoft.Advisor/" in url:
            return (ArmPageEnvelope(url, ({"id": "/advisor/1", "properties": {"recommendationStatus": "New"}},)),)
        if "ResourceHealth" in url:
            return (ArmPageEnvelope(url, ({"id": "/health/1", "properties": {"status": "Active"}},)),)
        return (ArmPageEnvelope(url, ({"id": "sub-a", "displayName": "A"},)),)

    def post_json(self, url, payload):
        self.post_calls.append((url, payload))
        return {"data": [{"id": "/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm"}]}


class HttpWithResponses:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.post_calls = []

    def post_json(self, url, payload):
        self.post_calls.append((url, payload))
        if not self.responses:
            raise AssertionError("unexpected Resource Graph request")
        return self.responses.pop(0)


class QueryHttp(Http):
    def post_json(self, url, payload):
        self.post_calls.append((url, payload))
        query = payload["query"]
        if "resourcecontainers" in query:
            return {"data": [{"subscriptionId": "sub-a", "subscriptionName": "A"}]}
        if "servicehealthresources" in query:
            return {
                "data": [
                    {
                        "id": "/subscriptions/sub-a/providers/Microsoft.ResourceHealth/events/track-1/impactedResources/1",
                        "subscriptionId": "sub-a",
                        "properties": {
                            "targetResourceId": "/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-1",
                            "targetResourceType": "Microsoft.Compute/virtualMachines",
                            "targetRegion": "West Europe",
                        },
                    }
                ]
            }
        return {
            "data": [
                {
                    "id": "/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-1",
                    "name": "vm-1",
                    "type": "Microsoft.Compute/virtualMachines",
                    "location": "westeurope",
                    "resourceGroup": "rg",
                    "subscriptionId": "sub-a",
                    "tags": {},
                }
            ]
        }


class RepeatingTokenHttp(Http):
    def post_json(self, url, payload):
        self.post_calls.append((url, payload))
        return {"data": [], "$skipToken": "same-token"}


def context() -> RunContext:
    request = RunRequest(ReportSelector.ALL, ("sub-a",), date(2026, 7, 31))
    return RunContext(
        run_id="run-1",
        as_of_date=date(2026, 7, 31),
        created_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
        request=request,
        scope=Scope(("sub-a",), mode="explicit"),
        catalog_identity=CatalogIdentity(1, "0" * 64),
        dependency_plan=DependencyPlan(("scope", "catalog", "advisor")),
    )


def test_advisor_source_preserves_recommendation_evidence_and_receipt() -> None:
    http = Http()
    acquisition = AdvisorApiSource(http).acquire(context())

    assert acquisition.receipt.source == "advisor"
    assert acquisition.receipt.api_version == "2025-01-01"
    assert acquisition.receipt.expected_subscriptions == 1
    assert acquisition.receipt.is_complete
    assert acquisition.records[0].payload["id"] == "/advisor/1"
    assert http.list_calls[0][1]["params"]["$filter"]


def test_service_health_source_uses_resource_health_endpoint() -> None:
    http = Http()
    acquisition = ResourceHealthApiSource(http).acquire(context())

    assert acquisition.receipt.source == "service-health"
    assert acquisition.records[0].payload["id"] == "/health/1"
    assert "Microsoft.ResourceHealth/events" in http.list_calls[0][0]


def test_resource_graph_source_posts_query_without_normalizing_rows() -> None:
    http = Http()
    result = ResourceGraphApiSource(http).lookup(context(), ("/resource/1",))

    assert result[0]["id"].endswith("/vm")
    assert http.post_calls[0][1]["subscriptions"] == ["sub-a"]
    assert "resources" in http.post_calls[0][1]["query"]


def test_resource_graph_lookup_projects_normalized_resource_fields() -> None:
    resource_id = "/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Web/sites/app"
    http = HttpWithResponses(
        {
            "data": [
                {
                    "resourceId": resource_id,
                    "name": "app",
                    "type": "Microsoft.Web/sites",
                    "subscriptionId": "sub-a",
                }
            ]
        }
    )

    ResourceGraphApiSource(http).lookup(context(), (resource_id,))

    query = http.post_calls[0][1]["query"]
    assert "tolower(id)" in query
    assert "resourceId = tolower(id)" in query
    assert "resourceGroup" in query
    assert "subscriptionId" in query


def test_resource_graph_lookup_batches_resource_ids() -> None:
    resource_ids = tuple(
        f"/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Web/sites/app-{index}"
        for index in range(101)
    )
    http = HttpWithResponses({"data": []}, {"data": []})

    ResourceGraphApiSource(http).lookup(context(), resource_ids)

    assert len(http.post_calls) == 2


def test_resource_graph_lookup_subscriptions_uses_resourcecontainers() -> None:
    http = HttpWithResponses({"data": [{"subscriptionId": "sub-a", "name": "DEV"}]})

    rows = ResourceGraphApiSource(http).lookup_subscriptions(context())

    assert rows == ({"subscriptionId": "sub-a", "name": "DEV"},)
    assert "resourcecontainers" in http.post_calls[0][1]["query"]
    assert "subscriptionId = tolower(subscriptionId)" in http.post_calls[0][1]["query"]
    assert "microsoft.resources/subscriptions" in http.post_calls[0][1]["query"].lower()


def test_resource_graph_lookup_subscriptions_rejects_repeated_continuation_tokens() -> None:
    http = HttpWithResponses(
        {"data": [], "$skipToken": "same-token"},
        {"data": [], "$skipToken": "same-token"},
    )

    with pytest.raises(ValueError, match="continuation token repeated"):
        ResourceGraphApiSource(http).lookup_subscriptions(context())


def test_resource_graph_lookup_subscriptions_rejects_non_string_continuation_tokens() -> None:
    http = HttpWithResponses({"data": [], "$skipToken": 0})

    with pytest.raises(ValueError, match="continuation token"):
        ResourceGraphApiSource(http).lookup_subscriptions(context())


def test_resource_graph_source_queries_subscription_inventory() -> None:
    http = QueryHttp()
    result = ResourceGraphApiSource(http).lookup_subscription_inventory(context())

    assert result[0]["subscriptionName"] == "A"
    query = http.post_calls[0][1]["query"]
    assert "resourcecontainers" in query
    assert "subscriptionId" in query
    assert "subscriptionName=name" in query


def test_resource_graph_source_queries_service_health_resources() -> None:
    http = QueryHttp()
    result = ResourceGraphApiSource(http).lookup_service_health_resources(context())

    properties = result[0]["properties"]
    assert properties["targetResourceId"].endswith("/vm-1")
    assert properties["targetResourceType"] == "Microsoft.Compute/virtualMachines"
    assert properties["targetRegion"] == "West Europe"
    query = http.post_calls[0][1]["query"]
    assert "servicehealthresources" in query
    assert "| project id, subscriptionId, properties" in query


def test_resource_graph_source_queries_verified_resource_metadata() -> None:
    http = QueryHttp()
    result = ResourceGraphApiSource(http).lookup_resources(
        context(), ("/subscriptions/sub-a/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm-1",)
    )

    assert result[0]["name"] == "vm-1"
    query = http.post_calls[0][1]["query"]
    assert "resources" in query
    assert "tolower(id) in" in query
    assert "project id, name, type, location, resourceGroup, subscriptionId, tags" in query


def test_resource_graph_source_does_not_query_all_resources_for_empty_ids() -> None:
    http = QueryHttp()

    assert ResourceGraphApiSource(http).lookup_resources(context(), ()) == ()
    assert http.post_calls == []


def test_resource_graph_source_rejects_repeated_skip_tokens() -> None:
    http = RepeatingTokenHttp()

    with pytest.raises(ValueError, match="continuation token repeated"):
        ResourceGraphApiSource(http).lookup_subscription_inventory(context())


def test_subscription_source_preserves_explicit_scope_without_network_call() -> None:
    http = Http()
    scope = SubscriptionApiSource(http).resolve(context().request)

    assert scope.subscription_ids == ("sub-a",)
    assert scope.mode == "explicit"
    assert http.list_calls == []
