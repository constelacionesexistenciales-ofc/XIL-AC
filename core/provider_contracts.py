"""Stable provider contracts for search and model adapters.

Contracts contain normalized metadata only; they do not persist prompts or queries.
Provider adapters must implement their own privacy, timeout and destination policies.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class SearchResult:
    title: str
    url: str
    domain: str
    snippet: str = ""
    published_at: str | None = None


@dataclass(frozen=True, slots=True)
class SearchResponse:
    provider: str
    retrieved_at: str
    results: tuple[SearchResult, ...]


@dataclass(frozen=True, slots=True)
class ModelResponse:
    provider: str
    model: str
    text: str
    duration_ms: int | None = None


class ResearchProvider(Protocol):
    """A source-retrieval adapter conforming to the XIL-AC contract."""

    provider_id: str

    def search(self, query: str, count: int = 5) -> SearchResponse:
        """Return normalized results or raise a provider-specific safe error."""
        ...


class InferenceProvider(Protocol):
    """A text-generation adapter; authorization and risk gates remain outside it."""

    provider_id: str
    local_only: bool

    def generate(self, prompt: str) -> ModelResponse:
        """Generate text without gaining permissions or executing tools."""
        ...
