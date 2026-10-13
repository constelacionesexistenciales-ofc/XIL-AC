import json

from playwright.sync_api import expect, sync_playwright

BASE_URL = "http://127.0.0.1:4174/"
SESSION_ID = "2f4d30ab-44e5-48df-8c6d-cdbad0f11d4b"
METRICS = [
    "availability",
    "action_capacity",
    "integration_capacity",
    "phenomenological_movement",
    "vitality_energy",
    "coping_availability",
]


def open_page():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch()
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(BASE_URL, wait_until="domcontentloaded")
    return playwright, browser, page


def test_session_indicator_explains_ne_and_has_no_case_text_field():
    playwright, browser, page = open_page()
    try:
        expect(page.get_by_role("heading", name="Observar el movimiento, no completar una lista.")).to_be_visible()
        expect(page.locator("#token")).to_be_visible()
        expect(page.locator("textarea")).to_have_count(0)
        expect(page.locator("[data-metric]")).to_have_count(6)
        expect(page.locator('[data-metric="availability"] option').first).to_have_text("NE")
        expect(page.get_by_text("no son un diagnóstico", exact=False)).to_be_visible()
    finally:
        browser.close()
        playwright.stop()


def test_live_capture_and_post_session_report_use_server_data():
    playwright, browser, page = open_page()
    snapshots = []

    def route_api(route):
        request = route.request
        path = request.url.split("/v1/session-movement/sessions", 1)[-1]
        if request.method == "POST" and path == "":
            route.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps({
                    "session_id": SESSION_ID,
                    "objective": "stabilization",
                    "created_at": "2026-10-13T12:00:00+00:00",
                    "status": "open",
                }),
            )
            return
        if request.method == "POST" and path.endswith("/snapshots"):
            item = request.post_data_json
            snapshots.append({
                "snapshot_id": "snap-" + str(len(snapshots) + 1),
                "phase": item["phase"],
                "source": item["source"],
                "scores": item["scores"],
                "created_at": "2026-10-13T12:05:00+00:00",
            })
            route.fulfill(
                status=201,
                content_type="application/json",
                body=json.dumps({"snapshot_id": snapshots[-1]["snapshot_id"], "phase": item["phase"]}),
            )
            return
        if request.method == "GET" and path == "/" + SESSION_ID:
            arrival = next((item for item in snapshots if item["phase"] == "arrival"), None)
            closing = next((item for item in snapshots if item["phase"] == "closing"), None)
            delta = None
            if arrival and closing:
                delta = {
                    key: closing["scores"][key] - arrival["scores"][key]
                    if closing["scores"][key] is not None and arrival["scores"][key] is not None
                    else None
                    for key in METRICS
                }
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps({
                    "session_id": SESSION_ID,
                    "objective": "stabilization",
                    "status": "closed" if closing else "open",
                    "created_at": "2026-10-13T12:00:00+00:00",
                    "closed_at": "2026-10-13T12:50:00+00:00" if closing else None,
                    "snapshots": snapshots,
                    "delta": delta,
                    "interpretation_notice": "Indicadores descriptivos; no son diagnóstico ni medida clínica validada.",
                    "report_block": "MOVIMIENTO DURANTE EL ENCUENTRO",
                }),
            )
            return
        route.fulfill(status=404, content_type="application/json", body='{"detail":"not found"}')

    try:
        page.route("**/v1/session-movement/sessions**", route_api)
        page.locator("#token").fill("test-token-not-a-real-secret")
        page.locator("#start").click()
        expect(page.locator("#sessionId")).to_have_text(SESSION_ID)

        page.locator('[data-metric="availability"]').select_option("1")
        page.locator('[data-metric="vitality_energy"]').select_option("1")
        page.locator("#saveSnapshot").click()
        expect(page.locator("#measureStatus")).to_contain_text("Registro guardado: arrival")

        page.locator('[data-phase="closing"]').click()
        page.locator('[data-metric="availability"]').select_option("3")
        page.locator('[data-metric="vitality_energy"]').select_option("3")
        page.locator('[data-metric="coping_availability"]').select_option("4")
        page.locator("#saveSnapshot").click()

        expect(page.locator("#reportContent")).to_be_visible()
        expect(page.locator("#reportSummary")).to_contain_text("Variación de vitalidad")
        expect(page.locator("#reportSummary")).to_contain_text("+2 puntos")
        expect(page.locator("#reportSummary")).to_contain_text("Disponibilidad para afrontar")
        expect(page.locator("#saveSnapshot")).to_be_disabled()
        assert [item["phase"] for item in snapshots] == ["arrival", "closing"]
    finally:
        browser.close()
        playwright.stop()
