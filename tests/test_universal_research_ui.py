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


def test_domain_options_match_adaptive_visual_content():
    values = set(re.findall(r'<option value="([^"]+)"', HTML))
    expected = {"science", "history", "technology", "business", "education", "cfe"}
    assert values == expected
    for domain in expected:
        assert f"{domain}:" in JS
    assert 'domain: domain.value' in JS


def test_live_search_discloses_limits_and_does_not_fake_synthesis():
    assert 'fetch("/v1/research"' in JS
    assert "XMLHttpRequest" not in JS
    assert "WebSocket" not in JS
    assert "La síntesis automática aún no está conectada" in JS
    assert "BRAVE_SEARCH_API_KEY" in DOC
    assert "not a static mockup presented as a working product" in DOC


def test_responsive_accessibility_and_reduced_motion_contract():
    assert "@media(max-width:650px)" in CSS
    assert "@media(max-width:1000px)" in CSS
    assert "@media(prefers-reduced-motion:reduce)" in CSS
    assert ":focus-visible" in CSS
    assert 'aria-live="polite"' in HTML
    assert 'autocomplete="off"' in HTML
    assert not re.search(r"font-size:\s*[^;]+/\s*\d", CSS)


def test_interactive_controls_use_real_handlers_and_safe_source_links():
    for control_id in ("newResearch", "copySummary", "researchForm"):
        assert f'id="{control_id}"' in HTML
    for selector in ('#newResearch', '#copySummary', 'form.addEventListener', 'makeSourceCard'):
        assert selector in JS
    assert 'rel = "noopener noreferrer"' in JS
    assert "localPrivacyPatterns" in JS
    assert "aria-busy" in JS
