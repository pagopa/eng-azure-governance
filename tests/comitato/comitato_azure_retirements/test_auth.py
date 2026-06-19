from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.comitato.comitato_azure_retirements.libs import auth


def test_get_management_token_prefers_explicit_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AZURE_BEARER_TOKEN", "  token-123  ")

    token = auth.get_management_token()

    assert token == "token-123"


def test_get_management_token_requires_az_when_env_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AZURE_BEARER_TOKEN", raising=False)
    monkeypatch.setattr(auth.shutil, "which", lambda _: None)

    with pytest.raises(RuntimeError, match="az CLI is required"):
        auth.get_management_token()


def test_get_management_token_reads_token_from_az_cli(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AZURE_BEARER_TOKEN", raising=False)
    monkeypatch.setattr(auth.shutil, "which", lambda _: "/usr/bin/az")

    def fake_run(*args, **kwargs):  # type: ignore[no-untyped-def]
        assert args[0][:3] == ["/usr/bin/az", "account", "get-access-token"]
        return SimpleNamespace(stdout='{"accessToken": "az-token"}')

    monkeypatch.setattr(auth.subprocess, "run", fake_run)

    token = auth.get_management_token()

    assert token == "az-token"


def test_get_management_token_fails_when_az_payload_has_no_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AZURE_BEARER_TOKEN", raising=False)
    monkeypatch.setattr(auth.shutil, "which", lambda _: "/usr/bin/az")
    monkeypatch.setattr(
        auth.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout="{}")
    )

    with pytest.raises(RuntimeError, match="Failed to obtain Azure bearer token"):
        auth.get_management_token()
