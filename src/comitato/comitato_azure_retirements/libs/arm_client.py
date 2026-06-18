"""Minimal ARM REST client with pagination support."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class ArmPageResult:
    items: list[dict[str, Any]]
    page_count: int


class ArmClient:
    def __init__(self, bearer_token: str, timeout_seconds: int = 60) -> None:
        self._token = bearer_token
        self._timeout_seconds = timeout_seconds

    def get_json(self, url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        if params:
            query = urllib.parse.urlencode(params)
            separator = "&" if "?" in url else "?"
            target = f"{url}{separator}{query}"
        else:
            target = url

        request = urllib.request.Request(
            target,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                content = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} for {target}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Network error for {target}: {exc.reason}") from exc

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSON response from {target}") from exc

    def post_json(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                content = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Network error for {url}: {exc.reason}") from exc

        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid JSON response from {url}") from exc

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
