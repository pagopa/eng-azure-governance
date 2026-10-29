"""Small, bounded, redacting HTTP transport for Azure Resource Manager."""

from __future__ import annotations

from dataclasses import dataclass
from threading import local
from time import perf_counter
from time import sleep as default_sleep
from typing import Any, Callable, Mapping
from urllib.parse import urlsplit

import requests
from requests import Session
from requests.exceptions import RequestException, Timeout

from ...acquisition.progress import download_context, download_scope, source_label
from ...ports import NullRunObserver, RunObserver, RuntimeEvent
from ..filesystem.arm_cache import ArmResponseCache, ResponseCacheError
from .azure_auth import AccessTokenProvider

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
        cache: ArmResponseCache | None = None,
    ) -> None:
        if timeout_seconds <= 0 or retry_attempts < 0 or backoff_seconds < 0:
            raise ValueError("invalid ARM HTTP policy")
        self._token_provider = token_provider
        self._timeout_seconds = timeout_seconds
        self._retry_attempts = retry_attempts
        self._backoff_seconds = backoff_seconds
        self._session = session
        self._thread_sessions = local()
        self._sleep = sleep
        self._user_agent = user_agent
        self._observer = observer or NullRunObserver()
        self._cache = cache

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
            with download_scope(page=len(pages) + 1):
                payload = self.get_json(current_url, current_params, run_id=run_id)
            current_params = None
            raw_items = payload.get(items_key, [])
            if not isinstance(raw_items, list) or any(
                not isinstance(item, Mapping) for item in raw_items
            ):
                raise ArmHttpError(
                    f"unsupported {items_key} response shape from {_safe_url(current_url)}"
                )
            next_url = payload.get("nextLink")
            if next_url is not None and not isinstance(next_url, str):
                raise ArmHttpError(
                    f"unsupported continuation shape from {_safe_url(current_url)}"
                )
            pages.append(
                ArmPageEnvelope(current_url, tuple(raw_items), next_url or None)
            )
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
        started = perf_counter()
        path = (
            self._cache.path_for(method, url, params, json_payload)
            if self._cache is not None
            else None
        )
        try:
            cached = (
                self._cache.read(path)
                if self._cache is not None and path is not None
                else None
            )
            if cached is not None:
                payload, downloaded_at = cached
                self._download_event(
                    "http_cache_hit",
                    "Reused cache",
                    url,
                    run_id,
                    payload=payload,
                    downloaded_at=downloaded_at,
                    elapsed_seconds=perf_counter() - started,
                )
                return payload
            payload = self._request_live(
                method, url, params=params, json_payload=json_payload, run_id=run_id
            )
            if (
                isinstance(payload, dict)
                and self._cache is not None
                and path is not None
            ):
                downloaded_at = self._cache.write(path, payload)
                self._download_event(
                    "http_cache_saved",
                    "Downloaded and cached",
                    url,
                    run_id,
                    payload=payload,
                    downloaded_at=downloaded_at,
                    elapsed_seconds=perf_counter() - started,
                )
            elif isinstance(payload, dict):
                self._download_event(
                    "http_request_completed",
                    "Downloaded",
                    url,
                    run_id,
                    payload=payload,
                    elapsed_seconds=perf_counter() - started,
                )
            return payload
        except ResponseCacheError as exc:
            raise ArmHttpError(str(exc)) from exc

    def _request_live(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str] | None = None,
        json_payload: Mapping[str, Any] | None = None,
        run_id: str = "",
    ) -> Any:
        self._download_event(
            "http_request_started",
            f"Downloading; timeout {self._timeout_seconds:g}s per attempt; "
            f"up to {self._retry_attempts + 1} attempts; remaining pages unknown",
            url,
            run_id,
        )
        token = self._token_provider.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": self._user_agent,
        }
        for attempt in range(self._retry_attempts + 1):
            try:
                response = self._get_session().request(
                    method,
                    url,
                    params=params,
                    json=json_payload,
                    headers=headers,
                    timeout=self._timeout_seconds,
                )
            except Timeout as exc:
                if attempt < self._retry_attempts:
                    self._wait_before_retry(method, url, run_id, attempt, "timeout")
                    continue
                raise ArmHttpError(f"ARM request timeout for {_safe_url(url)}") from exc
            except RequestException as exc:
                raise ArmHttpError(
                    f"ARM transport failure for {_safe_url(url)}"
                ) from exc
            status = int(getattr(response, "status_code", 0))
            if status in RETRYABLE_STATUS_CODES and attempt < self._retry_attempts:
                self._wait_before_retry(method, url, run_id, attempt, status)
                continue
            if status < 200 or status >= 300:
                if status in RETRYABLE_STATUS_CODES:
                    raise ArmHttpError(
                        f"ARM request retry budget exhausted for {_safe_url(url)}"
                    )
                raise ArmHttpError(
                    f"ARM request returned HTTP {status} for {_safe_url(url)}"
                )
            try:
                return response.json()
            except (ValueError, TypeError) as exc:
                raise ArmHttpError(
                    f"malformed JSON response from {_safe_url(url)}"
                ) from exc
        raise ArmHttpError("ARM request retry budget exhausted")

    def _get_session(self) -> Session:
        if self._session is not None:
            return self._session
        if not hasattr(self._thread_sessions, "session"):
            self._thread_sessions.session = requests.Session()
        return self._thread_sessions.session

    def _wait_before_retry(
        self, method: str, url: str, run_id: str, attempt: int, status: int | str
    ) -> None:
        self._download_event(
            "http_retry",
            f"Retrying after {status}; next attempt {attempt + 2}/{self._retry_attempts + 1}; "
            f"backoff {self._backoff_seconds * (attempt + 1):g}s",
            url,
            run_id,
            level="WARNING",
            method=method,
            status=status,
            attempt=attempt + 1,
            retry_budget=self._retry_attempts,
        )
        self._sleep(self._backoff_seconds * (attempt + 1))

    def _download_event(
        self,
        event: str,
        action: str,
        url: str,
        run_id: str,
        *,
        payload: Mapping[str, Any] | None = None,
        downloaded_at: str = "",
        elapsed_seconds: float = 0,
        level: str = "INFO",
        **extra: object,
    ) -> None:
        context = dict(download_context())
        segments = urlsplit(url).path.strip("/").split("/")
        lowered = [part.casefold() for part in segments]
        source = str(
            context.get("source")
            or (
                "advisor"
                if "microsoft.advisor" in lowered
                else "service-health"
                if "microsoft.resourcehealth" in lowered
                else "azure"
            )
        )
        label = source_label(source)
        operation = str(context.get("operation") or segments[-1])
        subscription_id = str(context.get("subscription_id", ""))
        if not subscription_id and "subscriptions" in lowered:
            index = lowered.index("subscriptions") + 1
            if index < len(segments):
                subscription_id = segments[index]
        identity = [label, operation]
        if context.get("stage"):
            identity.append(str(context["stage"]))
        if subscription_id:
            identity.append(f"subscription {subscription_id}")
        number, total = (
            context.get("subscription_number"),
            context.get("subscription_total"),
        )
        if isinstance(number, int) and isinstance(total, int):
            identity.append(f"{number}/{total} subscriptions")
        batch_number, batch_total = (
            context.get("batch_number"),
            context.get("batch_total"),
        )
        if isinstance(batch_number, int) and isinstance(batch_total, int):
            identity.append(f"batch {batch_number}/{batch_total}")
        page = context.get("page", 1)
        identity.append(f"page {page}")
        details = [action]
        if payload is not None:
            items = payload.get("value", payload.get("data"))
            if isinstance(items, list):
                details.append(f"{len(items)} records")
            has_next = bool(
                payload.get("nextLink")
                or payload.get("$skipToken")
                or payload.get("skipToken")
            )
            if has_next:
                details.append("more pages pending (total unknown)")
            elif isinstance(batch_number, int) and isinstance(batch_total, int):
                details.append("last page of batch")
                remaining_batches = batch_total - batch_number
                context["remaining_batches"] = remaining_batches
                details.append(f"remaining batches {remaining_batches}")
            else:
                details.append("last page")
            if isinstance(number, int) and isinstance(total, int):
                completed = number - int(has_next)
                remaining = total - completed
                context["remaining_subscriptions"] = remaining
                details.append(f"remaining subscriptions {remaining}")
                acquisition_started = context.get("acquisition_started")
                if (
                    not has_next
                    and completed > 0
                    and remaining > 0
                    and isinstance(acquisition_started, float)
                ):
                    eta = (perf_counter() - acquisition_started) / completed * remaining
                    details.append(
                        f"estimated remaining {eta:.1f}s (main acquisition only)"
                    )
                    context["estimated_remaining_seconds"] = eta
            details.append(f"elapsed {elapsed_seconds:.1f}s")
        if downloaded_at:
            details.append(f"downloaded at {downloaded_at}")
        self._observer.emit(
            RuntimeEvent(
                level,
                event,
                f"[{' | '.join(identity)}] {'; '.join(details)}",
                run_id,
                {
                    **context,
                    "source": source,
                    "operation": operation,
                    "subscription_id": subscription_id,
                    "page": page,
                    "url": _safe_url(url),
                    "elapsed_seconds": elapsed_seconds,
                    "downloaded_at": downloaded_at,
                    **extra,
                },
            )
        )


__all__ = [
    "ArmHttpClient",
    "ArmHttpError",
    "ArmPageEnvelope",
    "RepeatedContinuationError",
]
