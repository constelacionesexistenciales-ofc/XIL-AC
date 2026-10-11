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
    assert handler.redirect_request(request, None, 302, "Found", {}, "http://api.search.brave.com/x") is None
    assert handler.redirect_request(request, None, 302, "Found", {}, "https://evil.example/x") is None
