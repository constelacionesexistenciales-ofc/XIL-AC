"""Evaluación transparente de metadatos de fuentes; no verifica la verdad del contenido."""
from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urlparse


def assess_source_metadata(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize provenance completeness and source diversity without inventing credibility.

    A domain count is not a reliability score. This function does not fetch pages,
    inspect article contents, verify authorship, or establish that claims are true.
    """
    valid_results = [item for item in results if isinstance(item, dict)]
    domains: list[str] = []
    https_count = 0
    missing_title_count = 0
    missing_domain_count = 0
    duplicate_url_count = 0
    seen_urls: set[str] = set()

    for item in valid_results:
        title = item.get("title")
        url = item.get("url")
        domain = item.get("domain")
        if not isinstance(title, str) or not title.strip():
            missing_title_count += 1
        if isinstance(url, str) and url:
            if url in seen_urls:
                duplicate_url_count += 1
            seen_urls.add(url)
            try:
                parsed = urlparse(url)
            except ValueError:
                parsed = None
            if parsed and parsed.scheme == "https" and parsed.hostname:
                https_count += 1
        if isinstance(domain, str) and domain.strip():
            domains.append(domain.strip().lower().rstrip("."))
        else:
            missing_domain_count += 1

    domain_counts = Counter(domains)
    unique_domains = len(domain_counts)
    if unique_domains == 0:
        diversity = "unavailable"
    elif unique_domains < 3:
        diversity = "insufficient"
    elif unique_domains < 5:
        diversity = "limited"
    else:
        diversity = "varied"

    return {
        "assessment_type": "provenance_metadata_only",
        "source_count": len(valid_results),
        "unique_domain_count": unique_domains,
        "domain_diversity": diversity,
        "https_source_count": https_count,
        "missing_title_count": missing_title_count,
        "missing_domain_count": missing_domain_count,
        "duplicate_url_count": duplicate_url_count,
        "reliability_score": None,
        "content_verified": False,
        "notice": (
            "La diversidad de dominios y los metadatos no prueban la fiabilidad "
            "de una fuente ni la exactitud de sus afirmaciones."
        ),
    }
