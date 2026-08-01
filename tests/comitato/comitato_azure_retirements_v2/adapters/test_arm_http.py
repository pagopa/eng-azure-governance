from __future__ import annotations

from dataclasses import dataclass

import pytest
import requests

from src.comitato.comitato_azure_retirements_v2.adapters.arm_http import (
    ArmHttpClient,
    ArmHttpError,
    RepeatedContinuationError,
)
from src.comitato.comitato_azure_retirements_v2.adapters.azure_auth import (
    AzureCliTokenProvider,
)
from src.comitato.comitato_azure_retirements_v2.ports import RuntimeEvent


@dataclass
class Response:
    status_code: int
    payload: object = None
    text: str = ""
    url: str = "https://management.azure.com/example"

    def json(self):
        if isinstance(self.payload, BaseException):
            raise self.payload
        return self.payload


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response
        return response


class Token:
    def get_token(self) -> str:
        return "secret-token"


@dataclass
class RecordingRunObserver:
    events: list[RuntimeEvent]

    def emit(self, event: RuntimeEvent) -> None:
        self.events.append(event)


def test_redacts_authorization_and_error_body() -> None:
    session = Session([Response(401, {"error": "secret-token"}, text="secret-token Authorization")])

    with pytest.raises(ArmHttpError) as caught:
        ArmHttpClient(Token(), session=session, sleep=lambda _: None).get_json("https://management.azure.com/x")

    message = str(caught.value)
    assert "secret-token" not in message
    assert "Authorization" not in message


def test_passes_central_timeout_and_translates_transport_errors() -> None:
    session = Session([requests.Timeout("secret-token")])

    with pytest.raises(ArmHttpError) as caught:
        ArmHttpClient(Token(), timeout_seconds=4, session=session, sleep=lambda _: None).get_json("https://management.azure.com/x")

    assert "timeout" in str(caught.value).casefold()
    assert "secret-token" not in str(caught.value)
    assert session.calls[0][2]["timeout"] == 4


def test_retries_throttling_with_a_bounded_policy() -> None:
    session = Session([Response(429), Response(200, {"value": [1]})])

    payload = ArmHttpClient(Token(), retry_attempts=1, session=session, sleep=lambda _: None).get_json("https://management.azure.com/x")

    assert payload == {"value": [1]}
    assert len(session.calls) == 2


def test_retry_emits_safe_event_without_query_or_credentials() -> None:
    observer = RecordingRunObserver([])
    session = Session([Response(429), Response(200, {"value": []})])
    client = ArmHttpClient(
        Token(),
        retry_attempts=1,
        backoff_seconds=0,
        session=session,
        sleep=lambda _: None,
        observer=observer,
    )

    assert client.get_json(
        "https://management.azure.com/subscriptions/sub-1?api-version=secret",
        run_id="run-1",
    ) == {"value": []}

    event = observer.events[0]
    assert event.event == "http_retry"
    assert event.run_id == "run-1"
    assert "api-version" not in str(event.context)
    assert "Bearer" not in str(event.context)


def test_reports_retry_exhaustion_without_sensitive_response_text() -> None:
    session = Session([Response(503, text="secret-token")] * 2)

    with pytest.raises(ArmHttpError, match="retry") as caught:
        ArmHttpClient(Token(), retry_attempts=1, session=session, sleep=lambda _: None).get_json("https://management.azure.com/x")

    assert "secret-token" not in str(caught.value)


@pytest.mark.parametrize("payload", ["not-json", {"value": "not-a-list"}])
def test_rejects_malformed_or_unsupported_json_shape(payload) -> None:
    actual = ValueError("malformed") if payload == "not-json" else payload
    session = Session([Response(200, actual)])
    if payload == "not-json":
        session.responses[0].payload = ValueError("malformed")

    with pytest.raises(ArmHttpError):
        ArmHttpClient(Token(), session=session, sleep=lambda _: None).list_pages("https://management.azure.com/x")


def test_traverses_continuations_and_rejects_repeated_tokens() -> None:
    session = Session([
        Response(200, {"value": [{"id": "one"}], "nextLink": "https://management.azure.com/x?page=2"}),
        Response(200, {"value": [{"id": "two"}]}, url="https://management.azure.com/x?page=2"),
    ])
    pages = ArmHttpClient(Token(), session=session, sleep=lambda _: None).list_pages("https://management.azure.com/x")
    assert [item for page in pages for item in page.items] == [{"id": "one"}, {"id": "two"}]
    assert len(pages) == 2

    repeated = Session([Response(200, {"value": [], "nextLink": "https://management.azure.com/x"})])
    with pytest.raises(RepeatedContinuationError):
        ArmHttpClient(Token(), session=repeated, sleep=lambda _: None).list_pages("https://management.azure.com/x")


def test_cli_token_provider_reads_environment_without_exposing_token(monkeypatch) -> None:
    monkeypatch.setenv("AZURE_BEARER_TOKEN", "secret-token")
    provider = AzureCliTokenProvider()

    assert provider.get_token() == "secret-token"
    assert "secret-token" not in repr(provider)
