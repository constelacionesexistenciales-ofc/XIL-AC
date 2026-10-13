"""Búsqueda web real para investigaciones generales, sin persistir consultas."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener


class _HTTPSProviderRedirectHandler(HTTPRedirectHandler):
    """Allow redirects only to the fixed HTTPS provider host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        try:
            parsed = urlparse(newurl)
            port = parsed.port
        except ValueError:
            return None
        if (
            parsed.scheme != "https"
            or parsed.hostname != "api.search.brave.com"
            or port not in (None, 443)
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
        ):
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class ResearchError(Exception):
    """Error seguro de búsqueda que no incluye consultas ni secretos."""


class ResearchProviderNotConfigured(ResearchError):
    pass


class ResearchProviderUnavailable(ResearchError):
    pass


class ResearchRateLimited(ResearchError):
    pass


_DOMAIN_HINTS = {
    "science": "scientific research studies evidence",
    "history": "historical sources archives primary sources",
    "technology": "technical documentation engineering",
    "business": "business industry market research",
    "education": "education teaching learning research",
    "cfe": "Constelaciones Familiares y Existenciales CFE",
}


def _query_for_domain(query: str, domain: str) -> str:
    """Apply a bounded search hint for the selected research domain."""
    if domain == "general":
        return query
    hint = _DOMAIN_HINTS.get(domain)
    if hint is None:
        raise ResearchProviderNotConfigured
    return f"{query} {hint}"


class _SameOriginRedirectHandler(HTTPRedirectHandler):
    """Allow redirects only to the configured search service origin."""

    def __init__(self, origin: tuple[str, str, int | None]) -> None:
        super().__init__()
        self._origin = origin

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        try:
            parsed = urlparse(newurl)
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
        except ValueError:
            return None
        if (
            parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
            or (parsed.scheme, parsed.hostname or "", port) != self._origin
        ):
            return None
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _search_searxng(query: str, count: int, domain: str = "general") -> dict:
    """Query an operator-controlled SearXNG instance; no API key is needed."""
    base_url = os.getenv("SEARXNG_BASE_URL", "http://searxng:8080").strip().rstrip("/")
    parsed_base = urlparse(base_url)
    try:
        configured_port = parsed_base.port
    except ValueError:
        raise ResearchProviderNotConfigured from None
    if (
        parsed_base.scheme not in {"http", "https"}
        or not parsed_base.hostname
        or parsed_base.username
        or parsed_base.password
        or parsed_base.query
        or parsed_base.fragment
        or (
            parsed_base.scheme == "http"
            and parsed_base.hostname not in {"searxng", "localhost", "127.0.0.1"}
        )
    ):
        raise ResearchProviderNotConfigured

    port = configured_port or (443 if parsed_base.scheme == "https" else 80)
    origin = (parsed_base.scheme, parsed_base.hostname, port)
    provider_query = _query_for_domain(query, domain)
    params = urlencode({"q": provider_query, "format": "json", "language": "auto"})
    request = Request(
        f"{base_url}/search?{params}",
        headers={"Accept": "application/json", "User-Agent": "XIL-AC-Research/0.5"},
        method="GET",
    )
    try:
        with build_opener(_SameOriginRedirectHandler(origin)).open(request, timeout=8) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ResearchProviderUnavailable
    except HTTPError as exc:
        if exc.code == 429:
            raise ResearchRateLimited from None
        raise ResearchProviderUnavailable from None
    except (URLError, TimeoutError, OSError, ValueError):
        raise ResearchProviderUnavailable from None

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ResearchProviderUnavailable from None
    raw_results = payload.get("results", []) if isinstance(payload, dict) else []
    if not isinstance(raw_results, list):
        raise ResearchProviderUnavailable

    seen: set[str] = set()
    results: list[dict[str, str | None]] = []
    for item in raw_results:
        if not isinstance(item, dict):
            continue
        title, url = item.get("title"), item.get("url")
        description = item.get("content", item.get("description", ""))
        if not isinstance(title, str) or not isinstance(url, str):
            continue
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or url in seen:
            continue
        seen.add(url)
        published = item.get("publishedDate")
        results.append(
            {
                "title": title[:300],
                "url": url[:2048],
                "domain": parsed.hostname[:255],
                "description": description[:1000] if isinstance(description, str) else "",
                "published_at": published[:100] if isinstance(published, str) else None,
            }
        )
        if len(results) >= max(1, min(count, 10)):
            break

    return {
        "provider": "self_hosted_searxng",
        "query": query,
        "domain": domain,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "result_count": len(results),
        "results": results,
    }


def search_web(query: str, count: int = 5, domain: str = "general") -> dict:
    """Consulta Brave Search API y devuelve metadatos normalizados.

    No registra la consulta ni guarda resultados. El proveedor solo se invoca
    después de autenticar, autorizar y pasar los controles de privacidad.
    """
    backend = os.getenv("RESEARCH_BACKEND", "brave").strip().lower()
    if backend == "searxng":
        return _search_searxng(query, count, domain)
    if backend != "brave":
        raise ResearchProviderNotConfigured

    api_key = os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
    if not api_key:
        raise ResearchProviderNotConfigured

    provider_query = _query_for_domain(query, domain)
    params = urlencode({"q": provider_query, "count": max(1, min(count, 10))})
    request = Request(
        f"https://api.search.brave.com/res/v1/web/search?{params}",
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
            "User-Agent": "XIL-AC-Research/0.5",
        },
        method="GET",
    )

    try:
        with build_opener(_HTTPSProviderRedirectHandler()).open(request, timeout=8) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ResearchProviderUnavailable
    except HTTPError as exc:
        if exc.code == 429:
            raise ResearchRateLimited from None
        raise ResearchProviderUnavailable from None
    except (URLError, TimeoutError, OSError):
        raise ResearchProviderUnavailable from None

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ResearchProviderUnavailable from None

    web = payload.get("web", {}) if isinstance(payload, dict) else {}
    raw_results = web.get("results", []) if isinstance(web, dict) else []
    if not isinstance(raw_results, list):
        raise ResearchProviderUnavailable

    seen: set[str] = set()
    results: list[dict[str, str | None]] = []
    for item in raw_results:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        url = item.get("url")
        description = item.get("description")
        if not isinstance(title, str) or not isinstance(url, str):
            continue
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or url in seen:
            continue
        seen.add(url)
        results.append(
            {
                "title": title[:300],
                "url": url[:2048],
                "domain": parsed.hostname[:255],
                "description": description[:1000] if isinstance(description, str) else "",
                "published_at": (
                    item.get("page_age")[:100]
                    if isinstance(item.get("page_age"), str)
                    else None
                ),
            }
        )
        if len(results) >= count:
            break

    return {
        "provider": "brave_search",
        "query": query,
        "domain": domain,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "result_count": len(results),
        "results": results,
    }
