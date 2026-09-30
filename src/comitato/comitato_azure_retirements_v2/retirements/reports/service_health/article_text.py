from __future__ import annotations

import re
from collections.abc import Mapping
from datetime import datetime
from html.parser import HTMLParser
from typing import Any

class _ArticleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.casefold() in {"p", "div", "li", "br", "h1", "h2", "h3"}:
            self.parts.append(" ")
        if tag.casefold() == "a":
            self.href = dict(attrs).get("href")

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "a" and self.href:
            self.parts.append(f" ({self.href})")
            self.href = None
        elif tag.casefold() in {"p", "div", "li", "br", "h1", "h2", "h3"}:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

def plain_article(value: Any) -> str:
    return plain_text(value)

def recommended_action_section(value: Any) -> str:
    if not isinstance(value, str) or not value:
        return ""
    section = re.search(
        r"(?is)<h[1-6]\b[^>]*>\s*recommended actions?(?:\s|&nbsp;|:)*</h[1-6]>(.*?)"
        r"(?=<h[1-6]\b|$)",
        value,
    )
    return plain_text(section.group(1)) if section else ""

def text_retirement_claim(
    properties: Mapping[str, Any], article: Mapping[str, Any]
) -> tuple[str, str]:
    sources = (
        ("properties.title", properties.get("title")),
        ("properties.description", properties.get("description")),
        ("properties.article.articleContent", article.get("articleContent")),
    )
    claims: list[tuple[str, str]] = []
    date_pattern = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
    month = r"January|February|March|April|May|June|July|August|September|October|November|December"
    written_date_pattern = re.compile(
        rf"\b(?:\d{{1,2}}\s+(?:{month})\s+\d{{4}}|(?:{month})\s+\d{{1,2}},?\s+\d{{4}})\b",
        re.IGNORECASE,
    )
    partial_date_pattern = re.compile(rf"\b(?:{month})\s+\d{{4}}\b", re.IGNORECASE)
    retirement_pattern = re.compile(r"\bretir(?:e|ed|ement|ing|es|al)\b", re.IGNORECASE)
    for source, raw_text in sources:
        text = plain_text(raw_text)
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            if not retirement_pattern.search(sentence):
                continue
            sentence_claims = [
                (match.group(), source) for match in date_pattern.finditer(sentence)
            ]
            for match in written_date_pattern.finditer(sentence):
                raw_date = match.group().replace(",", "")
                formats = ("%d %B %Y", "%B %d %Y")
                for date_format in formats:
                    try:
                        parsed = datetime.strptime(raw_date, date_format).date()
                    except ValueError:
                        continue
                    sentence_claims.append((parsed.isoformat(), source))
                    break
            if not sentence_claims:
                partial_match = partial_date_pattern.search(sentence)
                if partial_match:
                    parsed = datetime.strptime(partial_match.group(), "%B %Y")
                    sentence_claims.append((parsed.strftime("%Y-%m"), source))
            claims.extend(sentence_claims)
    dates = {value for value, _ in claims}
    if len(dates) > 1:
        source_paths = ",".join(sorted({source for _, source in claims}))
        return "conflict:" + ",".join(sorted(dates)), "conflicting:" + source_paths
    if not claims:
        return "", ""
    value = claims[0][0]
    source_paths = ",".join(sorted({source for _, source in claims}))
    return value, source_paths

def plain_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Mapping):
        if not value:
            return ""
        value = (
            value.get("actionText")
            or value.get("description")
            or value.get("name")
            or value.get("articleContent")
            or ""
        )
    if isinstance(value, (list, tuple)):
        return " ".join(item for item in (plain_text(part) for part in value) if item)
    text = str(value)
    if "<" in text and ">" in text:
        parser = _ArticleParser()
        parser.feed(text)
        text = "".join(parser.parts)
    return " ".join(text.split())

__all__ = ["plain_article", "plain_text", "recommended_action_section", "text_retirement_claim"]
