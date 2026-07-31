from pathlib import Path


def read_current_tree(destination: Path) -> dict[str, bytes]:
    reference = (destination / "current").read_text(encoding="utf-8").strip()
    current = destination / reference
    return {
        path.relative_to(current).as_posix(): path.read_bytes()
        for path in sorted(current.rglob("*"))
        if path.is_file()
    }
