"""Atomic, non-expiring cache of successful Azure response objects."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


class ResponseCacheError(RuntimeError):
    pass


def _encoded(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


class ArmResponseCache:
    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def path_for(
        self,
        method: str,
        url: str,
        params: Mapping[str, str] | None,
        payload: Mapping[str, Any] | None,
    ) -> Path:
        request = {"method": method, "url": url, "params": params, "payload": payload}
        return self.directory / f"{sha256(_encoded(request)).hexdigest()}.json"

    def read(self, path: Path) -> tuple[dict[str, Any], str] | None:
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise ResponseCacheError(
                f"Cannot read Azure response cache: {path}"
            ) from exc
        try:
            entry = json.loads(data)
            if (
                not isinstance(entry, dict)
                or entry.get("schema_version") != 1
                or entry.get("request_sha256") != path.stem
                or not isinstance(entry.get("payload"), dict)
                or not isinstance(entry.get("downloaded_at"), str)
                or not entry["downloaded_at"]
                or entry.get("payload_sha256")
                != sha256(_encoded(entry["payload"])).hexdigest()
            ):
                raise ValueError("invalid cache entry")
            return entry["payload"], entry["downloaded_at"]
        except (ValueError, TypeError) as exc:
            raise ResponseCacheError(
                f"Invalid Azure response cache: {path}; remove this entry to download it again"
            ) from exc

    def write(self, path: Path, payload: dict[str, Any]) -> str:
        downloaded_at = datetime.now(timezone.utc).isoformat()
        entry = {
            "schema_version": 1,
            "request_sha256": path.stem,
            "downloaded_at": downloaded_at,
            "payload_sha256": sha256(_encoded(payload)).hexdigest(),
            "payload": payload,
        }
        temporary_path: Path | None = None
        try:
            self.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb", dir=self.directory, prefix=".download-", delete=False
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(_encoded(entry))
                handle.flush()
                os.fsync(handle.fileno())
            temporary_path.replace(path)
        except OSError as exc:
            raise ResponseCacheError(
                f"Cannot save Azure response cache: {path}"
            ) from exc
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
        return downloaded_at
