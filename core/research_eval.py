"""Deterministic offline metrics for comparing research providers.

This module scores retrieved URLs against human-authored reference judgments.
It does not judge semantic truth and must not be presented as a full research-quality score.
"""
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class ResearchCase:
    case_id: str
    relevant_domains: frozenset[str]
    forbidden_domains: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class CaseMetrics:
    case_id: str
    retrieved: int
    relevant: int
    precision_at_k: float
    recall_at_k: float
    forbidden_results: int
    invalid_urls: int


def _domain(url: object) -> str | None:
    if not isinstance(url, str):
        return None
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return None
    return parsed.hostname.lower().rstrip(".")


def evaluate_case(
    case: ResearchCase,
    results: list[dict[str, object]],
    *,
    k: int = 5,
) -> CaseMetrics:
    """Score the first k results; domain judgments must be curated by a reviewer."""
    if k < 1:
        raise ValueError("k must be positive")
    selected = results[:k]
    domains = [_domain(item.get("url")) for item in selected]
    valid_domains = [domain for domain in domains if domain is not None]
    relevant = sum(domain in case.relevant_domains for domain in valid_domains)
    forbidden = sum(
        domain in case.forbidden_domains for domain in valid_domains
    )
    relevant_total = len(case.relevant_domains)
    precision = relevant / len(selected) if selected else 0.0
    recall = min(1.0, relevant / relevant_total) if relevant_total else 0.0
    return CaseMetrics(
        case_id=case.case_id,
        retrieved=len(selected),
        relevant=relevant,
        precision_at_k=precision,
        recall_at_k=recall,
        forbidden_results=forbidden,
        invalid_urls=len(selected) - len(valid_domains),
    )


def aggregate_metrics(metrics: list[CaseMetrics]) -> dict[str, float | int]:
    """Return macro averages and safety counts for a benchmark report."""
    if not metrics:
        return {
            "cases": 0,
            "mean_precision_at_k": 0.0,
            "mean_recall_at_k": 0.0,
            "forbidden_results": 0,
            "invalid_urls": 0,
        }
    size = len(metrics)
    return {
        "cases": size,
        "mean_precision_at_k": sum(item.precision_at_k for item in metrics) / size,
        "mean_recall_at_k": sum(item.recall_at_k for item in metrics) / size,
        "forbidden_results": sum(item.forbidden_results for item in metrics),
        "invalid_urls": sum(item.invalid_urls for item in metrics),
    }
