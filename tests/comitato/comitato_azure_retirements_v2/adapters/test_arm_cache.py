import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Barrier, get_ident
from time import perf_counter
from types import SimpleNamespace

import pytest
import requests

from src.comitato.comitato_azure_retirements_v2.retirements.acquisition.progress import (
    download_context,
    download_scope,
)
from src.comitato.comitato_azure_retirements_v2.retirements.adapters.azure.arm_http import (
    ArmHttpError,
)
from src.comitato.comitato_azure_retirements_v2.retirements.adapters.azure.azure_auth import (
    AzureCliTokenProvider,
)
from src.comitato.comitato_azure_retirements_v2.retirements.application.composition import (
    build_application,
)
from src.comitato.comitato_azure_retirements_v2.retirements.config import (
    HttpPolicy,
    RuntimeConfig,
)
from src.comitato.comitato_azure_retirements_v2.retirements.domain.execution import (
    ReportSelector,
    RunRequest,
)
from src.comitato.comitato_azure_retirements_v2.retirements.domain.platforms import (
    PlatformAssignment,
    PlatformCatalogSnapshot,
    SubscriptionId,
)
from src.comitato.comitato_azure_retirements_v2.retirements.ports import RuntimeEvent

URL = "https://management.azure.com/subscriptions/sub-a/providers/Microsoft.ResourceHealth/events"


@dataclass
class JsonResponse:
    payload: object
    status_code: int = 200

    def json(self) -> object:
        return self.payload


class ScriptedSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return JsonResponse(value)


class Observer:
    def __init__(self):
        self.events: list[RuntimeEvent] = []

    def emit(self, event):
        self.events.append(event)


@pytest.fixture
def application_factory(tmp_path, monkeypatch):
    monkeypatch.setattr(AzureCliTokenProvider, "get_token", lambda _: "test-token")

    def build(responses, observer=None):
        session = ScriptedSession(responses)
        monkeypatch.setattr(requests, "Session", lambda: session)
        config = RuntimeConfig(
            request=RunRequest(ReportSelector.ALL),
            output_path=tmp_path,
            http=HttpPolicy(retry_attempts=0),
        )
        return build_application(config, observer=observer), session

    return build


def test_reuses_download_across_process_compositions_without_new_requests(
    application_factory, tmp_path
):
    application, session = application_factory([{"value": [{"id": "event-1"}]}])
    assert application.service_health_source.http.get_json(URL) == {
        "value": [{"id": "event-1"}]
    }

    observer = Observer()
    restarted, offline_session = application_factory([], observer)
    assert restarted.service_health_source.http.get_json(URL) == {
        "value": [{"id": "event-1"}]
    }
    assert len(session.calls) == 1
    assert offline_session.calls == []
    assert any(event.event == "http_cache_hit" for event in observer.events)
    assert "downloaded_at" in observer.events[-1].context
    assert "test-token" not in "".join(
        path.read_text() for path in tmp_path.rglob("*.json")
    )


@pytest.mark.parametrize(
    "first,second",
    [
        ({"params": {"api-version": "1"}}, {"params": {"api-version": "2"}}),
        ({"params": {"page": "1"}}, {"params": {"page": "2"}}),
    ],
)
def test_cache_separates_request_parameters(application_factory, first, second):
    application, session = application_factory([{"value": [1]}, {"value": [2]}])
    http = application.advisor_source.http
    assert http.get_json(URL, **first) == {"value": [1]}
    assert http.get_json(URL, **second) == {"value": [2]}
    assert http.get_json(URL, **first) == {"value": [1]}
    assert len(session.calls) == 2


def test_cache_separates_subscriptions_methods_and_resource_graph_bodies(
    application_factory,
):
    application, session = application_factory(
        [{"value": [1]}, {"value": [2]}, {"data": [3]}, {"data": [4]}]
    )
    http = application.advisor_source.http
    assert http.get_json(URL) == {"value": [1]}
    assert http.get_json(URL.replace("sub-a", "sub-b")) == {"value": [2]}
    assert http.post_json(URL, {"subscriptions": ["sub-a"]}) == {"data": [3]}
    assert http.post_json(URL, {"subscriptions": ["sub-b"]}) == {"data": [4]}
    assert http.post_json(URL, {"subscriptions": ["sub-a"]}) == {"data": [3]}
    assert len(session.calls) == 4


def test_failed_page_is_not_cached_and_completed_page_survives(
    application_factory,
):
    next_url = URL + "?page=2"
    application, session = application_factory(
        [{"value": [{"id": "one"}], "nextLink": next_url}, requests.Timeout()]
    )
    with pytest.raises(ArmHttpError, match="timeout"):
        application.service_health_source.http.list_pages(URL)

    restarted, retry_session = application_factory([{"value": [{"id": "two"}]}])
    pages = restarted.service_health_source.http.list_pages(URL)
    assert [item["id"] for page in pages for item in page.items] == ["one", "two"]
    assert len(session.calls) == 2
    assert [call[1] for call in retry_session.calls] == [next_url]


def test_corrupt_cache_fails_explicitly_and_removal_triggers_download(
    application_factory, tmp_path: Path
):
    application, _ = application_factory([{"value": []}])
    application.advisor_source.http.get_json(URL)
    entries = list((tmp_path / ".acquisition-cache").glob("*.json"))
    assert len(entries) == 1
    entries[0].write_text("corrupt", encoding="utf-8")

    restarted, session = application_factory([{"value": [{"id": "fresh"}]}])
    with pytest.raises(ArmHttpError, match="cache"):
        restarted.advisor_source.http.get_json(URL)
    assert session.calls == []

    entries[0].unlink()
    assert restarted.advisor_source.http.get_json(URL) == {"value": [{"id": "fresh"}]}


def test_scope_resolution_is_not_cached(application_factory):
    application, session = application_factory(
        [{"value": [{"subscriptionId": "sub-a"}]}] * 2
    )
    request = RunRequest(ReportSelector.ALL)
    assert application.scope_source.resolve(request).subscription_ids == ("sub-a",)
    assert application.scope_source.resolve(request).subscription_ids == ("sub-a",)
    assert len(session.calls) == 2


def test_default_transport_uses_a_separate_session_per_acquisition_thread(
    tmp_path, monkeypatch
):
    barrier = Barrier(2)
    sessions = []
    monkeypatch.setattr(AzureCliTokenProvider, "get_token", lambda _: "test-token")

    class ThreadSession(ScriptedSession):
        def __init__(self):
            super().__init__([{"value": []}])
            self.thread_id = get_ident()
            sessions.append(self)

        def request(self, method, url, **kwargs):
            assert get_ident() == self.thread_id
            barrier.wait(timeout=2)
            return super().request(method, url, **kwargs)

    monkeypatch.setattr(requests, "Session", ThreadSession)
    application = build_application(
        RuntimeConfig(request=RunRequest(ReportSelector.ALL), output_path=tmp_path)
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(application.advisor_source.http.get_json, URL + f"?page={page}")
            for page in (1, 2)
        ]
        assert [future.result() for future in futures] == [{"value": []}, {"value": []}]
    assert len(sessions) == 2


def test_cache_checksum_detects_modified_payload(application_factory, tmp_path):
    application, session = application_factory([{"value": []}])
    application.advisor_source.http.get_json(URL)
    entry_path = next((tmp_path / ".acquisition-cache").glob("*.json"))
    entry = json.loads(entry_path.read_text())
    entry["payload"] = {"value": [{"id": "changed"}]}
    entry_path.write_text(json.dumps(entry))

    with pytest.raises(ArmHttpError, match="cache"):
        application.advisor_source.http.get_json(URL)
    assert len(session.calls) == 1


def test_cache_write_failure_is_explicit_and_leaves_no_partial_entry(
    application_factory, tmp_path, monkeypatch
):
    application, session = application_factory([{"value": []}])

    def fail_replace(self, target):
        raise OSError("disk unavailable")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(ArmHttpError, match="Cannot save Azure response cache"):
        application.advisor_source.http.get_json(URL)

    assert len(session.calls) == 1
    assert list((tmp_path / ".acquisition-cache").iterdir()) == []


def test_full_report_reuses_main_downloads_metadata_and_enrichment(
    tmp_path, monkeypatch
):
    subscription_id = "11111111-1111-1111-1111-111111111111"
    calls = []

    class AzureSession:
        def request(self, method, url, **kwargs):
            calls.append((method, url))
            if url == "https://management.azure.com/subscriptions":
                payload = {"value": [{"subscriptionId": subscription_id}]}
            elif method == "POST":
                payload = {
                    "data": [
                        {"subscriptionId": subscription_id, "name": "Subscription A"}
                    ]
                }
            else:
                payload = {"value": []}
            return JsonResponse(payload)

    monkeypatch.setattr(requests, "Session", AzureSession)
    monkeypatch.setattr(AzureCliTokenProvider, "get_token", lambda _: "test-token")
    config = RuntimeConfig(
        request=RunRequest(ReportSelector.ALL),
        output_path=tmp_path / "exports",
        committee_yaml_path=tmp_path / "committee.yaml",
    )
    catalog = PlatformCatalogSnapshot(
        1,
        "a" * 64,
        (
            PlatformAssignment(
                SubscriptionId(subscription_id), "Test", "Subscription A"
            ),
        ),
    )
    dependencies = {"catalog_source": SimpleNamespace(load=lambda: catalog)}
    cold = build_application(config, dependencies=dependencies).run(config.request)
    assert cold.exit_status == 0
    cold_calls = len(calls)
    assert cold_calls == 5

    warm = build_application(config, dependencies=dependencies).run(config.request)
    assert warm.exit_status == 0
    assert calls[cold_calls:] == [("GET", "https://management.azure.com/subscriptions")]
    assert [
        (artifact.logical_path, artifact.data) for artifact in warm.candidate.artifacts
    ] == [
        (artifact.logical_path, artifact.data) for artifact in cold.candidate.artifacts
    ]


def test_download_messages_identify_source_subscription_page_and_remaining_work(
    application_factory,
):
    observer = Observer()
    application, _ = application_factory(
        [
            {"value": [{"id": "one"}], "nextLink": URL + "?page=2"},
            {"value": [{"id": "two"}]},
        ],
        observer,
    )
    http = application.service_health_source.http
    http.list_pages(URL, run_id="run-1")
    saved = [event for event in observer.events if event.event == "http_cache_saved"]
    assert len(saved) == 2
    assert all("Service Health" in event.message for event in saved)
    assert all("sub-a" in event.message for event in saved)
    assert "page 1" in saved[0].message
    assert "page 2" in saved[1].message
    assert "more pages" in saved[0].message
    assert "last page" in saved[1].message
    assert all("elapsed" in event.message for event in saved)
    assert any(event.event == "http_request_started" for event in observer.events)
    assert all("page=2" not in event.message for event in observer.events)

    http.list_pages(URL, run_id="run-1")
    hits = [event for event in observer.events if event.event == "http_cache_hit"]
    assert all(
        "Service Health" in event.message and "sub-a" in event.message for event in hits
    )
    assert all("downloaded at" in event.message for event in hits)


def test_remaining_subscriptions_and_eta_are_scoped_to_main_acquisition(
    application_factory,
):
    observer = Observer()
    application, _ = application_factory([{"value": []}], observer)
    with download_scope(
        source="service-health",
        stage="1/2 main acquisition",
        subscription_number=1,
        subscription_total=3,
        acquisition_started=perf_counter() - 2,
    ):
        application.service_health_source.http.list_pages(URL)

    completed = next(
        event for event in observer.events if event.event == "http_cache_saved"
    )
    assert completed.context["remaining_subscriptions"] == 2
    assert "remaining subscriptions 2" in completed.message
    assert "estimated remaining" in completed.message
    assert "(main acquisition only)" in completed.message
    assert "1/3 subscriptions" in completed.message
    assert download_context() == {}


def test_concurrent_download_identities_do_not_leak_between_sources(
    application_factory,
):
    observer = Observer()
    application, _ = application_factory([{"value": []}, {"value": []}], observer)
    barrier = Barrier(2)

    def download(source):
        with download_scope(
            source=source, operation="Resource Graph resource inventory"
        ):
            barrier.wait(timeout=2)
            application.advisor_source.http.get_json(URL + f"?source={source}")
        return download_context()

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(download, source) for source in ("advisor", "service-health")
        ]
        assert [future.result() for future in futures] == [{}, {}]
    saved = [event for event in observer.events if event.event == "http_cache_saved"]
    assert {event.context["source"] for event in saved} == {"advisor", "service-health"}
    for event in saved:
        expected = (
            "Advisor" if event.context["source"] == "advisor" else "Service Health"
        )
        assert event.message.startswith(
            f"[{expected} | Resource Graph resource inventory"
        )
