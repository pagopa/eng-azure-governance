"""Authentication helpers for Azure ARM calls."""

from __future__ import annotations

import json
import os
import shutil
import subprocess


def get_management_token() -> str:
    explicit = os.getenv("AZURE_BEARER_TOKEN", "").strip()
    if explicit:
        return explicit

    az_cli = shutil.which("az")
    if not az_cli:
        raise RuntimeError(
            "az CLI is required for live mode unless AZURE_BEARER_TOKEN is provided"
        )

    result = subprocess.run(
        [
            az_cli,
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
    token = payload.get("accessToken", "").strip()
    if not token:
        raise RuntimeError("Failed to obtain Azure bearer token from az CLI")
    return token
