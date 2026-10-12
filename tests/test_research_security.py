import pytest

import core.research as research


@pytest.mark.parametrize(
    "base_url",
    [
        "http://169.254.169.254/latest/meta-data",
        "http://192.168.1.20:8080",
        "http://10.0.0.8:8080",
        "http://[::1]:8080",
        "http://user:pass@searxng:8080",
        "http://searxng:8080/?next=https://example.org",
        "http://searxng:8080/#fragment",
        "https://user:pass@search.example.org",
        "ftp://searxng:8080",
        "http://searxng:not-a-port",
    ],
)
def test_searxng_rejects_untrusted_or_malformed_base_urls_before_network(
    monkeypatch, base_url
):
    monkeypatch.setenv("RESEARCH_BACKEND", "searxng")
    monkeypatch.setenv("SEARXNG_BASE_URL", base_url)

    def network_must_not_start(*_args, **_kwargs):
        raise AssertionError("network access attempted before URL validation")

    monkeypatch.setattr(research, "build_opener", network_must_not_start)

    with pytest.raises(research.ResearchProviderNotConfigured):
        research.search_web("synthetic public query")


@pytest.mark.parametrize(
    "target",
    [
        "https://searxng:8080/search",
        "http://searxng:8081/search",
        "http://127.0.0.1:8080/search",
        "http://user@searxng:8080/search",
    ],
)
def test_searxng_redirect_handler_rejects_origin_changes(monkeypatch, target):
    handler = research._SameOriginRedirectHandler(("http", "searxng", 8080))
    request = research.Request("http://searxng:8080/search")

    rejected = handler.redirect_request(request, None, 302, "Found", {}, target)

    assert rejected is None

def test_searxng_redirect_handler_allows_same_origin_without_credentials():
    handler = research._SameOriginRedirectHandler(("http", "searxng", 8080))
    request = research.Request("http://searxng:8080/search")

    redirected = handler.redirect_request(
        request, None, 302, "Found", {}, "http://searxng:8080/results"
    )

    assert redirected is not None
