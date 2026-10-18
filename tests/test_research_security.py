"""Regression tests for the public research egress gate and SearXNG URL handling.

These tests intentionally use synthetic queries and never make network requests.
"""
from types import SimpleNamespace
from urllib.request import Request

import pytest

import core.research as research


def test_public_query_requires_explicit_confirmation(monkeypatch):
    monkeypatch.setenv("RESEARCH_BACKEND", "searxng")

    def network_must_not_start(*_args, **_kwargs):
        raise AssertionError("network access attempted before public-query confirmation")

    monkeypatch.setattr(research, "build_opener", network_must_not_start)

    with pytest.raises(research.ResearchPrivacyGateRejected):
        research.search_web("synthetic public query")


def test_sensitive_query_is_rejected_before_provider_egress(monkeypatch):
    monkeypatch.setenv("RESEARCH_BACKEND", "searxng")
    monkeypatch.setattr(
        research,
        "detect_research_sensitive_content",
        lambda _query: SimpleNamespace(should_warn=True),
    )

    def network_must_not_start(*_args, **_kwargs):
        raise AssertionError("network access attempted for a rejected query")

    monkeypatch.setattr(research, "build_opener", network_must_not_start)

    with pytest.raises(research.ResearchPrivacyGateRejected):
        research.search_web("synthetic sensitive query", confirmed_public_query=True)


@pytest.mark.parametrize(
    "base_url",
    [
        "ftp://searxng:8080",
        "http://user:pass@searxng:8080",
        "http://@searxng:8080",
        "http://searxng:8080/?next=https://example.org",
        "http://searxng:8080/#fragment",
        "http://search.example.org:8080",
        "http://searxng:not-a-port",
    ],
)
def test_untrusted_or_malformed_searxng_base_url_is_rejected_before_network(
    monkeypatch, base_url
):
    monkeypatch.setenv("RESEARCH_BACKEND", "searxng")
    monkeypatch.setenv("SEARXNG_BASE_URL", base_url)
    monkeypatch.setattr(
        research,
        "detect_research_sensitive_content",
        lambda _query: SimpleNamespace(should_warn=False),
    )

    def network_must_not_start(*_args, **_kwargs):
        raise AssertionError("network access attempted before URL validation")

    monkeypatch.setattr(research, "build_opener", network_must_not_start)

    with pytest.raises(research.ResearchProviderNotConfigured):
        research.search_web("synthetic public query", confirmed_public_query=True)


@pytest.mark.parametrize(
    "target",
    [
        "https://searxng:8080/search",
        "http://searxng:8081/search",
        "http://127.0.0.1:8080/search",
        "http://user@searxng:8080/search",
        "http://searxng:8080/search#fragment",
    ],
)
def test_searxng_redirect_handler_rejects_origin_or_url_changes(target):
    handler = research._SameOriginRedirectHandler(("http", "searxng", 8080))
    request = Request("http://searxng:8080/search")

    assert handler.redirect_request(request, None, 302, "Found", {}, target) is None


def test_searxng_redirect_handler_allows_same_origin_without_credentials():
    handler = research._SameOriginRedirectHandler(("http", "searxng", 8080))
    request = Request("http://searxng:8080/search")

    redirected = handler.redirect_request(
        request, None, 302, "Found", {}, "http://searxng:8080/results"
    )

    assert redirected is not None
