"""Búsqueda web real para investigaciones generales, sin persistir consultas."""

from __future__ import annotations

import ipaddress
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
            valid_port = parsed.port in (None, 443)
        except ValueError:
            return None
        if (
            parsed.scheme != "https"
            or parsed.hostname != "api.search.brave.com"
            or parsed.username is not None
            or parsed.password is not None
            or not valid_port
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


def _safe_result_url(value: str) -> tuple[str, str] | None:
    """Accept only bounded public HTTPS URLs suitable for display as sources.

    Search results are not fetched by this function. The checks also avoid
    presenting credential-bearing, nonstandard-port, or local-network URLs as
    ordinary research sources.
    """
    if not value or len(value) > 2048 or any(ord(char) < 32 for char in value):
        return None
    if any(char.isspace() for char in value):
        return None
    try:
        parsed = urlparse(value)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
    ):
        return None

    hostname = hostname.rstrip(".").lower()
    if (
        hostname == "localhost"
        or hostname.endswith((".localhost", ".local", ".internal"))
    ):
        return None
    try:
        address = ipaddress.ip_address(hostname.strip("[]"))
    except ValueError:
        address = None
    if address is not None and (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    ):
        return None

    return value, hostname


def search_web(query: str, count: int = 5) -> dict:
    """Consulta Brave Search API y devuelve metadatos normalizados.

    No registra la consulta ni guarda resultados. El proveedor solo se invoca
    después de autenticar, autorizar y pasar los controles de privacidad.
    """
    api_key = os.getenv("BRAVE_SEARCH_API_KEY", "").strip()
    if not api_key:
        raise ResearchProviderNotConfigured

    safe_count = max(1, min(count, 10))
    params = urlencode({"q": query, "count": safe_count})
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
        safe_url = _safe_result_url(url)
        if safe_url is None:
            continue
        normalized_url, hostname = safe_url
        if normalized_url in seen:
            continue
        seen.add(normalized_url)
        results.append(
            {
                "title": title[:300],
                "url": normalized_url,
                "domain": hostname[:255],
                "description": description[:1000] if isinstance(description, str) else "",
                "published_at": (
                    item.get("page_age")[:100]
                    if isinstance(item.get("page_age"), str)
                    else None
                ),
            }
        )
        if len(results) >= safe_count:
            break

    return {
        "provider": "brave_search",
        "query": query,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "result_count": len(results),
        "results": results,
    }
