from core.privacy_detector import detect_sensitive_content


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
