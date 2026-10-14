from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from tools.validation_core import RepositorySnapshot


def test_snapshot_capture_keeps_logical_git_state_without_status_contents(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[list[str]] = []
    outputs = iter(("feature/validation-ux\n", "abc123\n", " M secret.tfvars\n"))

    def fake_run(args, **kwargs):
        calls.append(list(args))
        return subprocess.CompletedProcess(args, 0, next(outputs), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    snapshot = RepositorySnapshot.capture(tmp_path)

    assert snapshot.branch == "feature/validation-ux"
    assert snapshot.commit == "abc123"
    assert snapshot.clean is False
    assert snapshot.status_digest == hashlib.sha256(b" M secret.tfvars\n").hexdigest()
    assert not hasattr(snapshot, "status_text")
    assert calls == [
        ["git", "-C", str(tmp_path), "rev-parse", "--abbrev-ref", "HEAD"],
        ["git", "-C", str(tmp_path), "rev-parse", "HEAD"],
        ["git", "-C", str(tmp_path), "status", "--porcelain"],
    ]


def test_snapshot_delta_distinguishes_clean_noop_from_dirty_repository(
    monkeypatch, tmp_path: Path
) -> None:
    outputs = iter(
        (
            "main\n",
            "before\n",
            "",
            "main\n",
            "after\n",
            " M tools/validation_core/models.py\n",
        )
    )

    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(args, 0, next(outputs), "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    before = RepositorySnapshot.capture(tmp_path)
    after = RepositorySnapshot.capture(tmp_path)
    delta = RepositorySnapshot.delta(before, after)

    assert before.clean is True
    assert after.clean is False
    assert delta.changed is True
    assert delta.branch_changed is False
    assert delta.commit_changed is True
    assert delta.clean_changed is True
    assert delta.status_changed is True
    assert delta.before_status_digest != delta.after_status_digest


def test_snapshot_capture_does_not_run_mutating_git_commands(
    monkeypatch, tmp_path: Path
) -> None:
    commands: list[str] = []

    def fake_run(args, **kwargs):
        commands.append(" ".join(args))
        output = "main\n" if args[-1] == "HEAD" else ""
        return subprocess.CompletedProcess(args, 0, output, "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    RepositorySnapshot.capture(tmp_path)

    assert all(command.startswith("git -C ") for command in commands)
    assert all(
        not any(
            word in command.split() for word in ("reset", "clean", "checkout", "stash")
        )
        for command in commands
    )
