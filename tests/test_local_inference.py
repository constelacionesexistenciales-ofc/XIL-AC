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
