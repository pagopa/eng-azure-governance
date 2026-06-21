"""Utility helpers for aggregate and slide workflow exports."""

from __future__ import annotations

import hashlib
import re
from datetime import date
from typing import Iterable
from urllib.parse import quote

from .dates import parse_possible_date

WHITESPACE_PATTERN = re.compile(r"\s+")
URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
DATE_CANDIDATE_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}|[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})"
)

TECHNOLOGY_HINTS = {
    "aks": "Azure Kubernetes Service",
    "kubernetes": "Azure Kubernetes Service",
    "cosmos": "Azure Cosmos DB",
    "redis": "Azure Cache for Redis",
    "key vault": "Azure Key Vault",
    "synapse": "Azure Synapse Analytics",
    "front door": "Azure Front Door",
    "application gateway": "Azure Application Gateway",
    "cdn": "Azure CDN",
    "api management": "Azure API Management",
    "app service": "Azure App Service",
    "storage": "Azure Storage",
}


def normalize_key(value: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", value.strip().lower())


def canonical_title(value: object) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    return WHITESPACE_PATTERN.sub(" ", text)


def sorted_unique(values: Iterable[object]) -> list[str]:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    return sorted(set(cleaned), key=str.lower)


def as_string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def first_non_empty(values: list[str]) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""


def pick_human_text(values: Iterable[object]) -> str:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    if not cleaned:
        return ""
    cleaned.sort(key=lambda value: (len(value), value.lower()), reverse=True)
    return cleaned[0]


def min_iso_date(values: Iterable[object]) -> str:
    valid_dates = sorted(str(value) for value in values if parse_possible_date(str(value)))
    return valid_dates[0] if valid_dates else ""


def max_iso_date(values: Iterable[object]) -> str:
    valid_dates = sorted(str(value) for value in values if parse_possible_date(str(value)))
    return valid_dates[-1] if valid_dates else ""


def build_advisory_key(
    *,
    advice_type: str,
    canonical_title_value: str,
    canonical_date: str,
    source_identifiers: object,
) -> str:
    base_key = f"{advice_type}|{canonical_title_value}|{canonical_date}"
    if canonical_title_value:
        return base_key

    identifiers = as_string_list(source_identifiers)
    digest = hashlib.sha1("|".join(identifiers).encode("utf-8")).hexdigest()[:12]
    return f"{base_key}|{digest}"


def extract_links(texts: Iterable[object]) -> list[str]:
    links: list[str] = []
    for text in texts:
        raw_text = str(text or "")
        if not raw_text:
            continue
        for link in URL_PATTERN.findall(raw_text):
            clean_link = link.rstrip('.,);"]')
            if clean_link:
                links.append(clean_link)
    return sorted_unique(links)


def portal_link_from_identifier(identifier: object) -> str:
    clean_identifier = str(identifier or "").strip()
    if not clean_identifier:
        return ""

    lower_identifier = clean_identifier.lower()
    if lower_identifier.startswith("https://") or lower_identifier.startswith("http://"):
        return clean_identifier

    if clean_identifier.startswith("/"):
        return f"https://portal.azure.com/#resource{quote(clean_identifier, safe='/')}"

    return f"https://portal.azure.com/#search/{quote(clean_identifier, safe='')}"


def traceable_links_from_identifiers(identifiers: Iterable[object]) -> list[str]:
    return sorted_unique(portal_link_from_identifier(identifier) for identifier in identifiers)


def infer_technology_from_text(*, candidates: Iterable[object]) -> str:
    merged_text = " ".join(str(candidate or "") for candidate in candidates).lower()
    if not merged_text.strip():
        return ""

    for needle, technology in TECHNOLOGY_HINTS.items():
        if needle in merged_text:
            return technology

    return ""


def priority_label(*, retirement_date: str, as_of_date: date) -> str:
    parsed_date = parse_possible_date(retirement_date)
    if parsed_date is None:
        return "Debito"

    days_to_retirement = (parsed_date - as_of_date).days
    if days_to_retirement <= 90:
        return "Critico"
    if days_to_retirement <= 180:
        return "Prioritario"
    if days_to_retirement <= 365:
        return "Da pianificare"
    return "Debito"
