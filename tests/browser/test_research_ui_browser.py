import json

from playwright.sync_api import expect, sync_playwright

BASE_URL = "http://127.0.0.1:4173/"
MOCK_PAYLOAD = {
    "status": "completed",
    "provider": "test-provider",
    "retrieved_at": "2026-10-10T12:00:00+00:00",
    "result_count": 1,
    "results": [
        {
            "title": "Fuente de prueba",
            "url": "https://example.org/evidence",
            "domain": "example.org",
            "description": "Descripción de evidencia de prueba.",
        }
    ],
}


def open_page():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch()
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(BASE_URL, wait_until="domcontentloaded")
    return playwright, browser, page


def test_search_renders_results_and_safe_links():
    playwright, browser, page = open_page()
    try:
        page.route(
            "**/v1/research",
            lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(MOCK_PAYLOAD),
            ),
        )
        page.locator("#researchQuestion").fill("Comparar dos tecnologías de búsqueda")
        page.locator("#accessToken").fill("test-token-not-a-real-secret")
        page.locator("#researchForm button[type=submit]").click()
        expect(page.locator("#resultTitle")).to_have_text(
            "Comparar dos tecnologías de búsqueda"
        )
        link = page.locator(".source-result-title")
        expect(link).to_have_text("Fuente de prueba")
        expect(link).to_have_attribute("rel", "noopener noreferrer")
        expect(page.locator("#summaryText")).to_contain_text(
            "No se generó una síntesis automática"
        )
    finally:
        browser.close()
        playwright.stop()


def test_sensitive_query_is_blocked_before_network_request():
    playwright, browser, page = open_page()
    requests = []

    def record_request(route):
        requests.append(route.request.url)
        route.abort()

    try:
        page.route("**/v1/research", record_request)
        page.locator("#researchQuestion").fill("consultante: María Pérez")
        page.locator("#accessToken").fill("test-token-not-a-real-secret")
        page.locator("#researchForm button[type=submit]").click()
        expect(page.locator("#summaryText")).to_contain_text(
            "no se envió a la API"
        )
        assert requests == []
    finally:
        browser.close()
        playwright.stop()


def test_provider_failure_does_not_show_fake_results():
    playwright, browser, page = open_page()
    try:
        page.route(
            "**/v1/research",
            lambda route: route.fulfill(
                status=503,
                content_type="application/json",
                body='{"detail":"unavailable"}',
            ),
        )
        page.locator("#researchQuestion").fill("Fuentes sobre búsqueda abierta")
        page.locator("#accessToken").fill("test-token-not-a-real-secret")
        page.locator("#researchForm button[type=submit]").click()
        expect(page.locator("#resultTitle")).to_have_text(
            "No se pudo completar la búsqueda"
        )
        expect(page.locator("#summaryText")).to_contain_text(
            "no está configurada"
        )
        expect(page.locator(".source-result-title")).to_have_count(0)
    finally:
        browser.close()
        playwright.stop()


def test_responsive_layout_has_no_horizontal_document_overflow():
    playwright, browser, page = open_page()
    try:
        viewports = [(360, 800), (390, 844), (768, 1024), (1024, 900), (1440, 1000)]
        for width, height in viewports:
            page.set_viewport_size({"width": width, "height": height})
            dimensions = page.evaluate(
                "() => ({viewport: document.documentElement.clientWidth, "
                "content: document.documentElement.scrollWidth})"
            )
            assert dimensions["content"] <= dimensions["viewport"], (
                f"Horizontal overflow at {width}px: {dimensions}"
            )
    finally:
        browser.close()
        playwright.stop()
