from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_graphify_repository_integration_contract() -> None:
    watcher = REPO_ROOT / "scripts" / "graphify-watch.sh"
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    attributes = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")

    assert watcher.is_file()
    assert watcher.stat().st_mode & 0o111
    assert "graphify-hooks:" in makefile
    assert "graphify-watch:" in makefile
    assert "graphify-update:" in makefile
    assert "graphify-out/graph.json merge=graphify" in attributes


def test_graphify_watcher_uses_repo_root_and_debounce() -> None:
    watcher = (REPO_ROOT / "scripts" / "graphify-watch.sh").read_text(encoding="utf-8")

    assert "git rev-parse --show-toplevel" in watcher
    assert "GRAPHIFY_WATCH_DEBOUNCE" in watcher
    assert "GRAPHIFY_MAX_WORKERS" in watcher
    assert "graphify.watch" in watcher


def test_graphify_make_targets_bound_worker_parallelism() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    assert "GRAPHIFY_MAX_WORKERS" in makefile
