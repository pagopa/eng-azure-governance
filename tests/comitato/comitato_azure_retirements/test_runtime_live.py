from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from src.comitato.comitato_azure_retirements.libs.config import RuntimeConfig
from src.comitato.comitato_azure_retirements.libs.diagnostics import DiagnosticsCollector
from src.comitato.comitato_azure_retirements.libs import runtime_live


class _Reporter:
    def section(self, *_args, **_kwargs) -> None:
        return None

    def step(self, *_args, **_kwargs) -> None:
        return None

    def success(self, *_args, **_kwargs) -> None:
        return None

    def observe_request(self, *_args, **_kwargs) -> None:
        return None


def _runtime_config(output_root: Path) -> RuntimeConfig:
    return RuntimeConfig(
        mode="live",
        workflows=["raw"],
        subscriptions=[],
        management_groups=["mg-core"],
        output_root=output_root,
        as_of_date=date(2026, 6, 21),
        health_query_start=date(2025, 1, 1),
        fixture_dir=None,
        write_raw_jsonl=False,
        allow_degraded=False,
        verbose=False,
        max_workers=4,
    )


def test_live_mode_raises_when_scope_resolves_to_no_subscriptions(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(runtime_live, "get_management_token", lambda: "token")
    monkeypatch.setattr(runtime_live, "ArmClient", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(
        runtime_live,
        "resolve_scope_subscriptions",
        lambda *_args, **_kwargs: ([], {}),
    )

    with pytest.raises(RuntimeError, match="No subscriptions resolved"):
        runtime_live.live_mode(
            cfg=_runtime_config(tmp_path),
            run_id="run-1",
            output_dir=tmp_path,
            diagnostics=DiagnosticsCollector("run-1"),
            reporter=_Reporter(),
            debug_logger=object(),
        )
