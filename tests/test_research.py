import json

import pytest

import core.research as research


def _search_public(*args, **kwargs):
    return research.search_web(*args, confirmed_public_query=True, **kwargs)


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, size=-1):
        return self.payload[:size]


class FakeOpener:
    def __init__(self, payload, captured=None):
        self.payload = payload
        self.captured = captured if captured is not None else {}

    def open(self, request, timeout):
        self.captured["url"] = request.full_url
        self.captured["timeout"] = timeout
        return FakeResponse(self.payload)


def test_search_web_requires_provider_secret(monkeypatch):
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    with pytest.raises(research.ResearchProviderNotConfigured):
        _search_public("climate adaptation")


def test_search_web_normalizes_https_results_and_deduplicates(monkeypatch):
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-provider-secret")
    payload = {
        "web": {
            "results": [
                {
                    "title": "A source",
                    "url": "https://example.org/source",
                    "description": "Evidence overview",
                    "page_age": "2026-09-01",
                },
                {
                    "title": "Duplicate",
                    "url": "https://example.org/source",
                    "description": "Duplicate result",
                },
                {
                    "title": "Unsafe",
                    "url": "http://unsafe.example/source",
                    "description": "Must be discarded",
                },
                {
                    "title": "Second source",
                    "url": "https://example.net/research",
                    "description": "Another result",
                },
            ]
        }
    }
    monkeypatch.setattr(research, "build_opener", lambda *handlers: FakeOpener(payload))

    result = _search_public("climate adaptation", count=5)

    assert result["provider"] == "brave_search"
    assert result["result_count"] == 2
    assert result["results"][0]["domain"] == "example.org"
    assert result["results"][0]["published_at"] == "2026-09-01"
    assert result["results"][1]["url"] == "https://example.net/research"


def test_search_web_caps_requested_result_count(monkeypatch):
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-provider-secret")
    captured = {}
    monkeypatch.setattr(
        research,
        "build_opener",
        lambda *handlers: FakeOpener({"web": {"results": []}}, captured),
    )

    result = _search_public("climate adaptation", count=50)

    assert "count=10" in captured["url"]
    assert captured["timeout"] == 8
    assert result["result_count"] == 0


def test_redirect_handler_rejects_non_https_and_other_hosts():
    handler = research._HTTPSProviderRedirectHandler()
    request = research.Request("https://api.search.brave.com/res/v1/web/search")
    insecure = handler.redirect_request(
        request, None, 302, "Found", {}, "http://api.search.brave.com/x"
    )
    external = handler.redirect_request(
        request, None, 302, "Found", {}, "https://evil.example/x"
    )
    assert insecure is None
    assert external is None


def test_self_hosted_searxng_search_needs_no_brave_key(monkeypatch):
    monkeypatch.setenv("RESEARCH_BACKEND", "searxng")
    monkeypatch.delenv("BRAVE_SEARCH_API_KEY", raising=False)
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://searxng:8080")
    payload = {
        "results": [
            {
                "title": "Primary source",
                "url": "https://example.org/paper",
                "content": "Research summary",
                "publishedDate": "2026-09-20",
            },
            {
                "title": "Unsafe result",
                "url": "http://example.org/insecure",
                "content": "Must be discarded",
            },
        ]
    }
    captured = {}
    monkeypatch.setattr(
        research,
        "build_opener",
        lambda *handlers: FakeOpener(payload, captured),
    )

    result = _search_public("public research question", count=5)

    assert result["provider"] == "self_hosted_searxng"
    assert result["result_count"] == 1
    assert result["results"][0]["title"] == "Primary source"
    assert "format=json" in captured["url"]
    assert captured["timeout"] == 8


def test_self_hosted_searxng_rejects_remote_plain_http(monkeypatch):
    monkeypatch.setenv("RESEARCH_BACKEND", "searxng")
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://search.example.org")
    with pytest.raises(research.ResearchProviderNotConfigured):
        _search_public("public research question")


def test_self_hosted_searxng_rejects_unknown_backend(monkeypatch):
    monkeypatch.setenv("RESEARCH_BACKEND", "unknown")
    with pytest.raises(research.ResearchProviderNotConfigured):
        _search_public("public research question")


def test_self_hosted_redirect_handler_rejects_cross_origin():
    handler = research._SameOriginRedirectHandler(("http", "searxng", 8080))
    request = research.Request("http://searxng:8080/search")
    rejected = handler.redirect_request(
        request, None, 302, "Found", {}, "http://other-service:8080/search"
    )
    assert rejected is None


def test_self_hosted_searxng_rejects_invalid_port(monkeypatch):
    monkeypatch.setenv("RESEARCH_BACKEND", "searxng")
    monkeypatch.setenv("SEARXNG_BASE_URL", "http://searxng:not-a-port")
    with pytest.raises(research.ResearchProviderNotConfigured):
        _search_public("public research question")


def test_self_hosted_redirect_handler_rejects_invalid_port():
    handler = research._SameOriginRedirectHandler(("http", "searxng", 8080))
    request = research.Request("http://searxng:8080/search")
    rejected = handler.redirect_request(
        request, None, 302, "Found", {}, "http://searxng:not-a-port/search"
    )
    assert rejected is None



def test_provider_boundary_requires_explicit_public_confirmation(monkeypatch):
    called = []
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "synthetic-provider-secret")
    monkeypatch.setattr(research, "build_opener", lambda *args: called.append(args))
    with pytest.raises(research.ResearchPrivacyGateRejected):
        research.search_web("climate adaptation")
    assert called == []


def test_provider_boundary_rechecks_sensitive_query(monkeypatch):
    called = []
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "synthetic-provider-secret")
    monkeypatch.setattr(research, "build_opener", lambda *args: called.append(args))
    with pytest.raises(research.ResearchPrivacyGateRejected):
        research.search_web(
            "Preparar el informe de sesión para paciente",
            confirmed_public_query=True,
        )
    assert called == []
