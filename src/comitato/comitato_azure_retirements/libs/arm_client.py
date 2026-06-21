"""ARM REST client with resilient retries and pagination support."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any

import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError, RequestException
from urllib3.util.retry import Retry


@dataclass
class ArmPageResult:
    items: list[dict[str, Any]]
    page_count: int


@dataclass(frozen=True)
class ArmRequestTrace:
    method: str
    url: str
    status_code: int
    retry_count: int


@dataclass(frozen=True)
class ArmClientSettings:
    timeout_seconds: int = 60
    retry_attempts: int = 5
    backoff_factor: float = 1.0
    backoff_jitter: float = 0.5
    # Default pool tracks the default worker cap used by runtime collectors.
    pool_connections: int = 16
    pool_maxsize: int = 16


DEFAULT_RETRY_STATUS_CODES = (408, 429, 500, 502, 503, 504)
DEFAULT_ALLOWED_METHODS = frozenset({"GET", "POST"})
DEFAULT_USER_AGENT = "eng-azure-governance/comitato-azure-retirements"
HTTP_ERROR_TEXT_MAX_CHARS = 512


def _compact_http_error_text(raw_text: str) -> str:
    normalized = " ".join(raw_text.split())
    if not normalized:
        return "<empty body>"
    if len(normalized) <= HTTP_ERROR_TEXT_MAX_CHARS:
        return normalized
    return normalized[:HTTP_ERROR_TEXT_MAX_CHARS] + " ... [truncated]"


def build_retry_policy(settings: ArmClientSettings | None = None) -> Retry:
    cfg = settings or ArmClientSettings()
    return Retry(
        total=cfg.retry_attempts,
        connect=cfg.retry_attempts,
        read=cfg.retry_attempts,
        status=cfg.retry_attempts,
        allowed_methods=DEFAULT_ALLOWED_METHODS,
        status_forcelist=DEFAULT_RETRY_STATUS_CODES,
        backoff_factor=cfg.backoff_factor,
        backoff_jitter=cfg.backoff_jitter,
        respect_retry_after_header=True,
        raise_on_status=False,
    )


def build_session(
    bearer_token: str, settings: ArmClientSettings | None = None
) -> Session:
    cfg = settings or ArmClientSettings()
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
        }
    )
    adapter = HTTPAdapter(
        max_retries=build_retry_policy(cfg),
        pool_connections=cfg.pool_connections,
        pool_maxsize=cfg.pool_maxsize,
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class ArmClient:
    def __init__(
        self,
        bearer_token: str,
        timeout_seconds: int = 60,
        settings: ArmClientSettings | None = None,
        session: Session | None = None,
        trace_handler: Callable[[ArmRequestTrace], None] | None = None,
    ) -> None:
        resolved_settings = settings or ArmClientSettings(timeout_seconds=timeout_seconds)
        if timeout_seconds != resolved_settings.timeout_seconds:
            resolved_settings = replace(resolved_settings, timeout_seconds=timeout_seconds)

        self._settings = resolved_settings
        self._timeout_seconds = resolved_settings.timeout_seconds
        self._session = session or build_session(bearer_token, resolved_settings)
        self._trace_handler = trace_handler

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = self._session.request(
                method,
                url,
                params=params,
                json=payload,
                timeout=self._timeout_seconds,
            )
        except RequestException as exc:
            target = exc.request.url if exc.request is not None else url
            raise RuntimeError(f"Network error for {target}: {exc}") from exc

        self._emit_trace(method, response)

        try:
            response.raise_for_status()
        except HTTPError as exc:
            error_text = _compact_http_error_text(response.text)
            raise RuntimeError(
                f"HTTP {response.status_code} for {response.url}: {error_text}"
            ) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise RuntimeError(f"Invalid JSON response from {response.url}") from exc

    def _emit_trace(self, method: str, response: Response) -> None:
        if self._trace_handler is None:
            return
        retries = getattr(getattr(response.raw, "retries", None), "history", ())
        self._trace_handler(
            ArmRequestTrace(
                method=method,
                url=response.url,
                status_code=response.status_code,
                retry_count=len(retries),
            )
        )

    def get_json(
        self, url: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        return self._request_json("GET", url, params=params)

    def post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request_json("POST", url, payload=payload)

    def list_with_nextlink(
        self,
        url: str,
        params: dict[str, str] | None = None,
        items_key: str = "value",
    ) -> ArmPageResult:
        all_items: list[dict[str, Any]] = []
        page_count = 0
        next_url: str | None = url
        next_params = params

        while next_url:
            payload = self.get_json(next_url, next_params)
            next_params = None
            page_count += 1
            page_items = payload.get(items_key, [])
            if isinstance(page_items, list):
                all_items.extend(page_items)
            next_url = payload.get("nextLink")

        return ArmPageResult(items=all_items, page_count=page_count)
