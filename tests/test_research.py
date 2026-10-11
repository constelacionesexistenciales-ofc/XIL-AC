import json

import pytest

import core.research as research


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
        research.search_web("climate adaptation")


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

    result = research.search_web("climate adaptation", count=5)

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

    result = research.search_web("climate adaptation", count=50)

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
    credentials = handler.redirect_request(
        request, None, 302, "Found", {},
        "https://user:password@api.search.brave.com/x",
    )
    unusual_port = handler.redirect_request(
        request, None, 302, "Found", {}, "https://api.search.brave.com:8443/x"
    )
    assert insecure is None
    assert external is None
    assert credentials is None
    assert unusual_port is None


@pytest.mark.parametrize(
    "url",
    [
        "http://example.org/source",
        "https://user:password@example.org/source",
        "https://example.org:8443/source",
        "https://localhost/admin",
        "https://service.local/path",
        "https://127.0.0.1/admin",
        "https://192.168.1.10/admin",
        "https://[::1]/admin",
        "https://example.org/has space",
        "https://example.org/" + "x" * 2050,
        "https://example.org:invalid/path",
    ],
)
def test_safe_result_url_rejects_unsafe_or_malformed_urls(url):
    assert research._safe_result_url(url) is None


@pytest.mark.parametrize(
    ("url", "hostname"),
    [
        ("https://example.org/research", "example.org"),
        ("https://example.org:443/research", "example.org"),
        ("https://8.8.8.8/research", "8.8.8.8"),
    ],
)
def test_safe_result_url_accepts_public_https_sources(url, hostname):
    assert research._safe_result_url(url) == (url, hostname)


def test_search_web_discards_urls_with_credentials_and_local_hosts(monkeypatch):
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-provider-secret")
    payload = {
        "web": {
            "results": [
                {"title": "Credential URL", "url": "https://user:pass@example.org/x"},
                {"title": "Local URL", "url": "https://localhost/admin"},
                {"title": "Valid source", "url": "https://example.org/source"},
            ]
        }
    }
    monkeypatch.setattr(research, "build_opener", lambda *handlers: FakeOpener(payload))

    result = research.search_web("climate adaptation", count=5)

    assert result["result_count"] == 1
    assert result["results"][0]["url"] == "https://example.org/source"


def test_search_web_rejects_malformed_results_collection(monkeypatch):
    monkeypatch.setenv("BRAVE_SEARCH_API_KEY", "test-provider-secret")
    monkeypatch.setattr(
        research,
        "build_opener",
        lambda *handlers: FakeOpener({"web": {"results": "not-a-list"}}),
    )

    with pytest.raises(research.ResearchProviderUnavailable):
        research.search_web("climate adaptation")
