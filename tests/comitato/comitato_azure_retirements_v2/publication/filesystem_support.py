from datetime import date
from pathlib import Path


def read_monthly_tree(destination: Path, as_of_date: date) -> dict[str, bytes]:
    current = destination / f"{as_of_date.year:04d}" / f"{as_of_date.month:02d}"
    return {
        path.relative_to(current).as_posix(): path.read_bytes()
        for path in sorted(current.rglob("*"))
        if path.is_file()
    }
