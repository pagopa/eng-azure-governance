"""Small, bounded, redacting HTTP transport for Azure Resource Manager."""

from __future__ import annotations

from dataclasses import dataclass
from time import sleep as default_sleep
from typing import Any, Callable, Mapping

import requests
from requests import Session
from requests.exceptions import RequestException, Timeout

from .azure_auth import AccessTokenProvider
from ..ports import NullRunObserver, RunObserver, RuntimeEvent


RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})


class ArmHttpError(RuntimeError):
    """Safe transport failure; it intentionally excludes response bodies."""


class RepeatedContinuationError(ArmHttpError):
    pass


@dataclass(frozen=True, slots=True)
class ArmPageEnvelope:
    url: str
    items: tuple[Mapping[str, Any], ...]
    continuation_url: str | None = None


def _safe_url(url: str) -> str:
    return url.split("?", 1)[0]


class ArmHttpClient:
    def __init__(
        self,
        token_provider: AccessTokenProvider,
        *,
        timeout_seconds: float = 60.0,
        retry_attempts: int = 3,
        backoff_seconds: float = 1.0,
        session: Session | None = None,
        sleep: Callable[[float], None] = default_sleep,
        user_agent: str = "eng-azure-governance/comitato-azure-retirements-v2",
        observer: RunObserver | None = None,
    ) -> None:
        if timeout_seconds <= 0 or retry_attempts < 0 or backoff_seconds < 0:
            raise ValueError("invalid ARM HTTP policy")
        self._token_provider = token_provider
        self._timeout_seconds = timeout_seconds
        self._retry_attempts = retry_attempts
        self._backoff_seconds = backoff_seconds
        self._session = session or requests.Session()
        self._sleep = sleep
        self._user_agent = user_agent
        self._observer = observer or NullRunObserver()

    def get_json(
        self,
        url: str,
        params: Mapping[str, str] | None = None,
        *,
        run_id: str = "",
    ) -> dict[str, Any]:
        payload = self._request("GET", url, params=params, run_id=run_id)
        if not isinstance(payload, dict):
            raise ArmHttpError(f"unsupported JSON response shape from {_safe_url(url)}")
        return payload

    def post_json(
        self,
        url: str,
        payload: Mapping[str, Any],
        *,
        run_id: str = "",
    ) -> dict[str, Any]:
        response = self._request("POST", url, json_payload=payload, run_id=run_id)
        if not isinstance(response, dict):
            raise ArmHttpError(f"unsupported JSON response shape from {_safe_url(url)}")
        return response

    def list_pages(
        self,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        items_key: str = "value",
        run_id: str = "",
    ) -> tuple[ArmPageEnvelope, ...]:
        pages: list[ArmPageEnvelope] = []
        visited: set[str] = set()
        current_url: str | None = url
        current_params = params
        while current_url:
            marker = current_url
            if marker in visited:
                raise RepeatedContinuationError("repeated continuation link")
            visited.add(marker)
            payload = self.get_json(current_url, current_params, run_id=run_id)
            current_params = None
            raw_items = payload.get(items_key, [])
            if not isinstance(raw_items, list) or any(not isinstance(item, Mapping) for item in raw_items):
                raise ArmHttpError(f"unsupported {items_key} response shape from {_safe_url(current_url)}")
            next_url = payload.get("nextLink")
            if next_url is not None and not isinstance(next_url, str):
                raise ArmHttpError(f"unsupported continuation shape from {_safe_url(current_url)}")
            pages.append(ArmPageEnvelope(current_url, tuple(raw_items), next_url or None))
            current_url = next_url or None
        return tuple(pages)

    def _request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        json_payload: Mapping[str, Any] | None = None,
        run_id: str = "",
    ) -> Any:
        token = self._token_provider.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": self._user_agent,
        }
        for attempt in range(self._retry_attempts + 1):
            try:
                response = self._session.request(
                    method,
                    url,
                    params=params,
                    json=json_payload,
                    headers=headers,
                    timeout=self._timeout_seconds,
                )
            except Timeout as exc:
                raise ArmHttpError(f"ARM request timeout for {_safe_url(url)}") from exc
            except RequestException as exc:
                raise ArmHttpError(f"ARM transport failure for {_safe_url(url)}") from exc
            status = int(getattr(response, "status_code", 0))
            if status in RETRYABLE_STATUS_CODES and attempt < self._retry_attempts:
                self._observer.emit(
                    RuntimeEvent(
                        "WARNING",
                        "http_retry",
                        "Retrying ARM request",
                        run_id,
                        {
                            "method": method,
                            "url": _safe_url(url),
                            "status": status,
                            "attempt": attempt + 1,
                            "retry_budget": self._retry_attempts,
                        },
                    )
                )
                self._sleep(self._backoff_seconds * (attempt + 1))
                continue
            if status < 200 or status >= 300:
                if status in RETRYABLE_STATUS_CODES:
                    raise ArmHttpError(f"ARM request retry budget exhausted for {_safe_url(url)}")
                raise ArmHttpError(f"ARM request returned HTTP {status} for {_safe_url(url)}")
            try:
                return response.json()
            except (ValueError, TypeError) as exc:
                raise ArmHttpError(f"malformed JSON response from {_safe_url(url)}") from exc
        raise ArmHttpError("ARM request retry budget exhausted")


__all__ = ["ArmHttpClient", "ArmHttpError", "ArmPageEnvelope", "RepeatedContinuationError"]
