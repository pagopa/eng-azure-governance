"""Normalize Service Health rich text for tabular exports."""

from __future__ import annotations

import re
import unicodedata
from html import unescape
from html.parser import HTMLParser
from urllib.parse import quote, unquote, urlsplit, urlunsplit

_BLOCK_TAGS = {"br", "div", "h1", "h2", "h3", "li", "ol", "p", "table", "tr", "ul"}
_PUNCTUATION = str.maketrans(
    {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
)


def _ascii_url(value: str) -> str:
    split = urlsplit(unescape(value).strip())
    return urlunsplit(
        (
            split.scheme,
            split.netloc.encode("idna").decode("ascii"),
            quote(unquote(split.path), safe="/:@"),
            quote(unquote(split.query), safe="=&/:@?"),
            quote(unquote(split.fragment), safe="=&/:@?"),
        )
    )


def _ascii_text(value: str) -> str:
    translated = unescape(value).translate(_PUNCTUATION)
    ascii_text = (
        unicodedata.normalize("NFKD", translated)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return ascii_text.replace("<", " less than ").replace(">", " greater than ")


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.anchor_href = ""
        self.anchor_parts: list[str] = []

    def _append_boundary(self) -> None:
        if self.anchor_href:
            self.anchor_parts.append(" ")
        else:
            self.parts.append(" ")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _BLOCK_TAGS:
            self._append_boundary()
        if tag != "a":
            return
        self.anchor_href = next(
            (value or "" for key, value in attrs if key == "href"), ""
        )
        self.anchor_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.anchor_href:
            anchor_text = "".join(self.anchor_parts)
            self.parts.append(anchor_text)
            ascii_url = _ascii_url(self.anchor_href)
            if anchor_text.strip() != ascii_url:
                self.parts.append(f" ({ascii_url})")
            self.anchor_href = ""
            self.anchor_parts = []
        if tag in _BLOCK_TAGS:
            self._append_boundary()

    def handle_data(self, data: str) -> None:
        value = _ascii_text(data)
        if self.anchor_href:
            self.anchor_parts.append(value)
        else:
            self.parts.append(value)


def html_to_ascii_text(value: str) -> str:
    if not value:
        return ""
    parser = _TextExtractor()
    parser.feed(value)
    parser.close()
    return re.sub(r"\s+", " ", "".join(parser.parts)).strip()
