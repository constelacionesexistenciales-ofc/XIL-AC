from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
QA_PATH = ROOT / "docs" / "LIVE_SESSION_ASSISTANT_QA.md"
SPEC_PATH = ROOT / "docs" / "LIVE_SESSION_ASSISTANT_SPEC.md"


def test_live_session_qa_inventory_has_unique_cases_through_live_22():
    qa = QA_PATH.read_text(encoding="utf-8")
    case_ids = re.findall(r"\| (LIVE-\d{2}) \|", qa)
    assert case_ids == [f"LIVE-{number:02d}" for number in range(1, 23)]
    assert len(case_ids) == len(set(case_ids))


def test_live_session_spec_protects_against_invented_personal_details():
    spec = SPEC_PATH.read_text(encoding="utf-8")
    assert "No inventar anécdotas" in spec
    assert "El humor es opcional" in spec
    assert "esperar evidencia nueva" in spec


def test_live_session_spec_keeps_unvalidated_hypotheses_open():
    spec = SPEC_PATH.read_text(encoding="utf-8")
    assert "Nunca elevar una hipótesis por repetición" in spec
    assert "insuficiente información en este fragmento" in spec
    assert "No se habilita procesamiento remoto" in spec


def test_qa_inventory_distinguishes_documentation_checks_from_behavioral_execution():
    qa = QA_PATH.read_text(encoding="utf-8")
    assert "no demuestra por sí solo que un modelo cumpla el comportamiento" in qa
    assert "No marcar un caso de comportamiento como aprobado" in qa
