"""Authentication ports and the live Azure CLI token provider."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Protocol


class AccessTokenProvider(Protocol):
    def get_token(self) -> str:
        ...


class AzureCliTokenProvider:
    """Read a short-lived ARM token without retaining it in runtime config."""

    def __init__(self, *, environment_name: str = "AZURE_BEARER_TOKEN") -> None:
        self._environment_name = environment_name

    def get_token(self) -> str:
        explicit = os.getenv(self._environment_name, "").strip()
        if explicit:
            return explicit
        executable = shutil.which("az")
        if not executable:
            raise RuntimeError("Azure authentication requires az CLI or AZURE_BEARER_TOKEN")
        try:
            result = subprocess.run(
                [
                    executable,
                    "account",
                    "get-access-token",
                    "--resource",
                    "https://management.azure.com/",
                    "--output",
                    "json",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            token = payload.get("accessToken", "") if isinstance(payload, dict) else ""
        except (OSError, subprocess.SubprocessError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError("Azure authentication failed") from exc
        if not isinstance(token, str) or not token.strip():
            raise RuntimeError("Azure authentication returned no usable token")
        return token.strip()

    def __call__(self) -> str:
        return self.get_token()


__all__ = ["AccessTokenProvider", "AzureCliTokenProvider"]
