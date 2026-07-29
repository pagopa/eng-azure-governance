from __future__ import annotations

from types import SimpleNamespace

import pytest
from requests.exceptions import HTTPError

from src.comitato.comitato_azure_retirements.libs.arm_client import (
    ArmClient,
    ArmClientSettings,
    ArmRequestTrace,
    build_retry_policy,
)


class FakeResponse:
    def __init__(
        self,
        *,
        url: str,
        status_code: int = 200,
        payload: dict | None = None,
        text: str = "",
        retry_count: int = 0,
        json_error: bool = False,
    ) -> None:
        self.url = url
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = text
        self._json_error = json_error
        self.raw = SimpleNamespace(
            retries=SimpleNamespace(history=[object()] * retry_count)
        )

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HTTPError(self.text)

    def json(self) -> dict:
        if self._json_error:
            raise ValueError("bad json")
        return self._payload


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self._responses = responses
        self.calls: list[dict[str, object]] = []

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        json: dict | None = None,
        timeout: int,
    ) -> FakeResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "params": params,
                "json": json,
                "timeout": timeout,
            }
        )
        return self._responses.pop(0)


def test_build_retry_policy_handles_429_and_retry_after() -> None:
    retry = build_retry_policy(ArmClientSettings(retry_attempts=7, backoff_factor=2.0))

    assert retry.total == 7
    assert retry.backoff_factor == 2.0
    assert retry.respect_retry_after_header is True
    assert 429 in retry.status_forcelist
    assert "GET" in retry.allowed_methods
    assert "POST" in retry.allowed_methods


def test_get_json_uses_session_with_params_and_timeout() -> None:
    session = FakeSession(
        [
            FakeResponse(
                url="https://example.test/items?api-version=1", payload={"value": 1}
            )
        ]
    )
    client = ArmClient("token", timeout_seconds=33, session=session)

    payload = client.get_json("https://example.test/items", params={"api-version": "1"})

    assert payload == {"value": 1}
    assert session.calls == [
        {
            "method": "GET",
            "url": "https://example.test/items",
            "params": {"api-version": "1"},
            "json": None,
            "timeout": 33,
        }
    ]


def test_list_with_nextlink_collects_all_pages() -> None:
    session = FakeSession(
        [
            FakeResponse(
                url="https://example.test/items?page=1",
                payload={
                    "value": [{"id": "a"}],
                    "nextLink": "https://example.test/items?page=2",
                },
            ),
            FakeResponse(
                url="https://example.test/items?page=2",
                payload={"value": [{"id": "b"}]},
            ),
        ]
    )
    client = ArmClient("token", session=session)

    page = client.list_with_nextlink("https://example.test/items")

    assert page.items == [{"id": "a"}, {"id": "b"}]
    assert page.page_count == 2


def test_get_json_wraps_http_errors() -> None:
    session = FakeSession(
        [
            FakeResponse(
                url="https://example.test/items",
                status_code=429,
                text="Too Many Requests",
            )
        ]
    )
    client = ArmClient("token", session=session)

    with pytest.raises(RuntimeError, match="HTTP 429"):
        client.get_json("https://example.test/items")


def test_get_json_truncates_and_sanitizes_http_error_text() -> None:
    long_error_text = "Too Many Requests\n" + ("x" * 1024)
    session = FakeSession(
        [
            FakeResponse(
                url="https://example.test/items",
                status_code=429,
                text=long_error_text,
            )
        ]
    )
    client = ArmClient("token", session=session)

    with pytest.raises(RuntimeError) as captured:
        client.get_json("https://example.test/items")

    message = str(captured.value)
    assert "HTTP 429" in message
    assert "Too Many Requests" in message
    assert "\n" not in message
    assert "... [truncated]" in message


def test_get_json_wraps_invalid_json() -> None:
    session = FakeSession(
        [FakeResponse(url="https://example.test/items", json_error=True)]
    )
    client = ArmClient("token", session=session)

    with pytest.raises(RuntimeError, match="Invalid JSON response"):
        client.get_json("https://example.test/items")


def test_trace_handler_receives_retry_history() -> None:
    traces: list[ArmRequestTrace] = []
    session = FakeSession(
        [
            FakeResponse(
                url="https://example.test/items", payload={"value": []}, retry_count=2
            )
        ]
    )
    client = ArmClient("token", session=session, trace_handler=traces.append)

    client.get_json("https://example.test/items")

    assert traces == [
        ArmRequestTrace(
            method="GET",
            url="https://example.test/items",
            status_code=200,
            retry_count=2,
        )
    ]
