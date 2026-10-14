import json

import pytest

import core.local_inference as local
from core.local_inference import LocalInferenceError, OllamaLocalProvider


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, size=-1):
        return self.payload[:size]


class FakeOpener:
    def __init__(self, payload):
        self.payload = payload
        self.request = None
        self.timeout = None

    def open(self, request, timeout):
        self.request = request
        self.timeout = timeout
        return FakeResponse(self.payload)


def test_local_provider_rejects_remote_hosts():
    with pytest.raises(LocalInferenceError):
        OllamaLocalProvider("model", "http://model.example:11434")


def test_local_provider_rejects_https_remote_url():
    with pytest.raises(LocalInferenceError):
        OllamaLocalProvider("model", "https://model.example")


def test_local_provider_normalizes_response_without_network(monkeypatch):
    opener = FakeOpener(json.dumps({"message": {"content": "respuesta local"}}).encode())
    monkeypatch.setattr(local, "build_opener", lambda *handlers: opener)
    provider = OllamaLocalProvider("model:small")
    result = provider.generate("Consulta sintética")
    assert result.text == "respuesta local"
    assert result.provider == "ollama_local"
    assert opener.timeout == 60.0
    assert json.loads(opener.request.data)["stream"] is False


def test_local_provider_rejects_empty_and_oversized_prompts():
    provider = OllamaLocalProvider("model:small")
    with pytest.raises(LocalInferenceError):
        provider.generate(" ")
    with pytest.raises(LocalInferenceError):
        provider.generate("x" * (provider.MAX_PROMPT_BYTES + 1))


def test_local_provider_rejects_malformed_response(monkeypatch):
    monkeypatch.setattr(local, "build_opener", lambda *handlers: FakeOpener(b"not json"))
    with pytest.raises(LocalInferenceError):
        OllamaLocalProvider("model:small").generate("synthetic")


@pytest.mark.parametrize(
    "url",
    [
        "http://192.0.2.10:11434",
        "http://[2001:db8::1]:11434",
        "http://localhost.attacker.example:11434",
        "http://ollama.attacker.example:11434",
        "http://user:secret@localhost:11434",
        "http://localhost:99999",
        "http://localhost:11434?target=attacker",
        "http://localhost:11434#fragment",
        "http://localhost:11434/other-path",
        "http://localhost:11434/api/chat",
        "http://localhost:11434/%2f%2fattacker.example",
    ],
)
def test_local_provider_rejects_ssrf_destination_variants(url):
    with pytest.raises(LocalInferenceError):
        OllamaLocalProvider("model", url)


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:11434",
        "http://localhost:11434",
        "http://[::1]:11434",
        "http://ollama:11434",
        "http://host.docker.internal:11434",
    ],
)
def test_local_provider_accepts_only_explicit_local_destinations(url):
    provider = OllamaLocalProvider("model", url)
    assert provider.base_url == url


def test_local_provider_rejects_oversized_response(monkeypatch):
    provider = OllamaLocalProvider("model:small")
    oversized = b"x" * (provider.MAX_RESPONSE_BYTES + 1)
    monkeypatch.setattr(
        local, "build_opener", lambda *handlers: FakeOpener(oversized)
    )
    with pytest.raises(LocalInferenceError, match="response_too_large"):
        provider.generate("synthetic prompt")


def test_local_provider_fails_closed_on_redirect(monkeypatch):
    from urllib.error import HTTPError

    class RedirectingOpener:
        def open(self, request, timeout):
            raise HTTPError(
                request.full_url,
                302,
                "Found",
                {"Location": "http://192.0.2.10:11434/api/chat"},
                None,
            )

    monkeypatch.setattr(local, "build_opener", lambda *handlers: RedirectingOpener())
    with pytest.raises(LocalInferenceError, match="local_model_unavailable"):
        OllamaLocalProvider("model:small").generate("synthetic prompt")
