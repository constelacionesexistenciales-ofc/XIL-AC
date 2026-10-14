"""Opt-in local Ollama adapter with destination and payload limits.

This adapter never falls back to a remote provider. It is not wired into session
processing and does not establish that a model is installed or performant.
"""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from core.provider_contracts import ModelResponse


class LocalInferenceError(RuntimeError):
    """Safe local-inference error; does not include prompts or secrets."""


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _validated_base_url(base_url: str) -> str:
    parsed = urlparse(base_url.strip())
    allowed_hosts = {"127.0.0.1", "localhost", "::1", "ollama", "host.docker.internal"}
    try:
        port = parsed.port
    except ValueError:
        raise LocalInferenceError("invalid_local_model_url") from None
    if (
        parsed.scheme != "http"
        or parsed.hostname not in allowed_hosts
        or parsed.username
        or parsed.password
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or port == 0
    ):
        raise LocalInferenceError("local_model_url_not_allowed")
    return base_url.strip().rstrip("/")


class OllamaLocalProvider:
    """Call an Ollama-compatible endpoint only on explicitly allowed local hosts."""

    provider_id = "ollama_local"
    local_only = True
    MAX_PROMPT_BYTES = 128_000
    MAX_RESPONSE_BYTES = 2_000_000

    def __init__(
        self,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        timeout_seconds: float = 60.0,
    ) -> None:
        if not model or len(model) > 200 or any(ord(char) < 32 for char in model):
            raise LocalInferenceError("invalid_model_identifier")
        if not 1 <= timeout_seconds <= 120:
            raise LocalInferenceError("invalid_timeout")
        self.model = model
        self.base_url = _validated_base_url(base_url)
        self.timeout_seconds = timeout_seconds

    def generate(self, prompt: str) -> ModelResponse:
        if not isinstance(prompt, str) or not prompt.strip():
            raise LocalInferenceError("empty_prompt")
        if len(prompt.encode("utf-8")) > self.MAX_PROMPT_BYTES:
            raise LocalInferenceError("prompt_too_large")

        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        started = time.monotonic()
        try:
            with build_opener(_NoRedirectHandler()).open(
                request, timeout=self.timeout_seconds
            ) as response:
                raw = response.read(self.MAX_RESPONSE_BYTES + 1)
                if len(raw) > self.MAX_RESPONSE_BYTES:
                    raise LocalInferenceError("response_too_large")
        except HTTPError as exc:
            if exc.code == 413:
                raise LocalInferenceError("request_rejected") from None
            raise LocalInferenceError("local_model_unavailable") from None
        except (URLError, TimeoutError, OSError):
            raise LocalInferenceError("local_model_unavailable") from None

        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise LocalInferenceError("invalid_local_model_response") from None
        message = data.get("message") if isinstance(data, dict) else None
        text = message.get("content") if isinstance(message, dict) else None
        if not isinstance(text, str):
            raise LocalInferenceError("invalid_local_model_response")
        return ModelResponse(
            provider=self.provider_id,
            model=self.model,
            text=text,
            duration_ms=max(0, int((time.monotonic() - started) * 1000)),
        )
