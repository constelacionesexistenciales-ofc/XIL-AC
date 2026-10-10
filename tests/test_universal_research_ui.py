from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "frontend" / "universal-research"
HTML = (UI / "index.html").read_text(encoding="utf-8")
CSS = (UI / "styles.css").read_text(encoding="utf-8")
JS = (UI / "app.js").read_text(encoding="utf-8")
DOC = (ROOT / "docs" / "UNIVERSAL_RESEARCH_EXPERIENCE.md").read_text(encoding="utf-8")


def test_html_has_spanish_mobile_shell_and_local_assets():
    assert '<html lang="es">' in HTML
    assert 'name="viewport"' in HTML
    assert 'href="./styles.css"' in HTML
    assert 'src="./app.js"' in HTML
    assert 'id="research"' in HTML
    assert 'id="sources"' in HTML


def test_domain_options_match_demo_content():
    values = set(re.findall(r'<option value="([^"]+)"', HTML))
    expected = {"science", "history", "technology", "business", "education", "cfe"}
    assert values == expected
    for domain in expected:
        assert f"{domain}:" in JS
    assert "No se ejecutó una investigación real" in JS


def test_demo_never_claims_to_fetch_real_research():
    assert "fetch(" not in JS
    assert "XMLHttpRequest" not in JS
    assert "WebSocket" not in JS
    assert "no contiene una investigación ejecutada" in HTML
    assert "no es un motor de investigación conectado" in DOC.lower()


def test_responsive_accessibility_and_reduced_motion_contract():
    assert "@media(max-width:650px)" in CSS
    assert "@media(max-width:1000px)" in CSS
    assert "@media(prefers-reduced-motion:reduce)" in CSS
    assert ":focus-visible" in CSS
    assert 'aria-live="polite"' in HTML
    assert 'aria-expanded="false"' in HTML
    assert not re.search(r"font-size:\s*[^;]+/\s*\d", CSS)


def test_interactive_controls_are_real_buttons_and_have_handlers():
    for control_id in ("newResearch", "copySummary", "researchForm"):
        assert f'id="{control_id}"' in HTML
    for selector in ("#newResearch", "#copySummary", "form.addEventListener", ".finding"):
        assert selector in JS
    assert "aria-expanded" in JS
