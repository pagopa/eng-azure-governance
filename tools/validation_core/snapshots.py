"""Read-only logical repository snapshots for validation evidence."""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path


def _git_output(root: Path, args: list[str]) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


@dataclass(frozen=True)
class RepositorySnapshot:
    root: Path
    branch: str
    commit: str
    clean: bool
    status_digest: str

    @classmethod
    def capture(cls, root: Path) -> "RepositorySnapshot":
        resolved_root = root.resolve()
        branch = _git_output(
            resolved_root, ["rev-parse", "--abbrev-ref", "HEAD"]
        ).strip()
        commit = _git_output(resolved_root, ["rev-parse", "HEAD"]).strip()
        status = _git_output(resolved_root, ["status", "--porcelain"])
        return cls(
            root=resolved_root,
            branch=branch,
            commit=commit,
            clean=not bool(status),
            status_digest=hashlib.sha256(status.encode("utf-8")).hexdigest(),
        )

    @property
    def status(self) -> str:
        return "clean" if self.clean else "dirty"

    @property
    def logical_status_digest(self) -> str:
        return self.status_digest

    def as_dict(self) -> dict[str, object]:
        return {
            "root": str(self.root),
            "branch": self.branch,
            "commit": self.commit,
            "clean": self.clean,
            "status": self.status,
            "status_digest": self.status_digest,
        }

    def delta(self, after: "RepositorySnapshot") -> "RepositoryDelta":
        return RepositoryDelta(
            changed=(
                self.branch != after.branch
                or self.commit != after.commit
                or self.clean != after.clean
                or self.status_digest != after.status_digest
            ),
            branch_changed=self.branch != after.branch,
            commit_changed=self.commit != after.commit,
            clean_changed=self.clean != after.clean,
            status_changed=self.status_digest != after.status_digest,
            before_status_digest=self.status_digest,
            after_status_digest=after.status_digest,
        )


@dataclass(frozen=True)
class RepositoryDelta:
    changed: bool
    branch_changed: bool
    commit_changed: bool
    clean_changed: bool
    status_changed: bool
    before_status_digest: str
    after_status_digest: str

    def as_dict(self) -> dict[str, object]:
        return {
            "changed": self.changed,
            "branch_changed": self.branch_changed,
            "commit_changed": self.commit_changed,
            "clean_changed": self.clean_changed,
            "status_changed": self.status_changed,
            "before_status_digest": self.before_status_digest,
            "after_status_digest": self.after_status_digest,
        }
