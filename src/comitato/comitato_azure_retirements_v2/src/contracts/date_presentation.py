from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime

_LINE_DATE = re.compile(
    r"(?m)^(?P<prefix>[ \t]*)(?P<date>\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})(?=\s|$)"
)
_SLASH_DATE = re.compile(r"(?m)^\s*(?P<first>\d{2})/(?P<second>\d{2})/\d{4}")


def detect_slash_date_style(values: Iterable[str]) -> str:
    has_italian_evidence = False
    has_us_evidence = False
    for value in values:
        for match in _SLASH_DATE.finditer(value):
            first = int(match.group("first"))
            second = int(match.group("second"))
            has_italian_evidence |= first > 12
            has_us_evidence |= second > 12
    if has_us_evidence and not has_italian_evidence:
        return "us"
    if has_us_evidence and has_italian_evidence:
        return "mixed"
    return "italian"


def format_italian_date_text(value: str, *, slash_style: str = "italian") -> str:
    if not value:
        return value

    def replace(match: re.Match[str]) -> str:
        raw = match.group("date")
        source_format = "%Y-%m-%d"
        if "/" in raw:
            first, second, _ = raw.split("/")
            if slash_style == "mixed":
                source_format = (
                    "%m/%d/%Y" if int(second) > 12 and int(first) <= 12 else "%d/%m/%Y"
                )
            elif slash_style == "us":
                source_format = "%m/%d/%Y"
            else:
                source_format = "%d/%m/%Y"
        try:
            rendered = datetime.strptime(raw, source_format).strftime("%d/%m/%Y")
        except ValueError:
            return match.group(0)
        return f"{match.group('prefix')}{rendered}"

    return _LINE_DATE.sub(replace, value)


def display_date_to_iso(value: str) -> str:
    for source_format in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, source_format).date().isoformat()
        except ValueError:
            continue
    return value


__all__ = [
    "detect_slash_date_style",
    "display_date_to_iso",
    "format_italian_date_text",
]
