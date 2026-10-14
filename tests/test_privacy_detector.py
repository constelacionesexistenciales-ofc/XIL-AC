import pytest

from core.privacy_detector import detect_research_sensitive_content, detect_sensitive_content


def test_detects_email_without_returning_the_value():
    finding = detect_sensitive_content("Contacto: alexis@example.com")
    assert finding.should_warn
    assert finding.risk in {"medium", "high"}
    assert "identificador_directo" in finding.categories
    assert "alexis@example.com" not in repr(finding)


def test_detects_labeled_name_and_clinical_information():
    finding = detect_sensitive_content(
        "Nombre completo: Persona Ejemplo. Tiene diagnóstico y medicación."
    )
    assert finding.should_warn
    assert finding.risk == "high"
    assert "identificador_directo" in finding.categories
    assert "informacion_de_salud" in finding.categories


def test_detects_high_sensitivity_terms():
    finding = detect_sensitive_content("La persona menciona ideación suicida.")
    assert finding.should_warn
    assert finding.risk == "high"
    assert "informacion_de_alta_sensibilidad" in finding.categories


def test_general_text_without_explicit_signals_is_not_flagged():
    finding = detect_sensitive_content(
        "Quiero investigar cómo se construyen las decisiones en los vínculos."
    )
    assert not finding.should_warn
    assert finding.risk == "no_signal_detected"


def test_empty_or_unverifiable_content_fails_cautiously():
    finding = detect_sensitive_content("   ")
    assert finding.should_warn
    assert finding.risk == "unknown"



@pytest.mark.parametrize(
    ("query", "expected_category"),
    [
        ("Contacto: persona-sintetica@example.invalid", "identificador_directo"),
        ("Mi diagnóstico requiere privacidad", "informacion_de_salud_personal"),
        ("Preparar el informe de sesión para consultante", "contenido_de_sesion"),
        ("Quiero hacerme daño", "informacion_de_alta_sensibilidad"),
    ],
)
def test_research_privacy_gate_blocks_synthetic_sensitive_queries(query, expected_category):
    finding = detect_research_sensitive_content(query)

    assert finding.should_warn
    assert expected_category in finding.categories
    assert query not in repr(finding)


@pytest.mark.parametrize(
    "query",
    [
        "Resumen de evidencia científica sobre salud pública",
        "Historia general de la psicología en el siglo XX",
        "Cómo se construyen las decisiones en los vínculos",
    ],
)
def test_research_privacy_gate_allows_general_nonpersonal_topics(query):
    finding = detect_research_sensitive_content(query)

    assert not finding.should_warn
    assert finding.risk == "no_signal_detected"
    assert finding.categories == ()


def test_research_privacy_gate_blocks_empty_or_unverifiable_query():
    finding = detect_research_sensitive_content("   ")

    assert finding.should_warn
    assert finding.risk == "unknown"
    assert "contenido_no_verificable" in finding.categories
