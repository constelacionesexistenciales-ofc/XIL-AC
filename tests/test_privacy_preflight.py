import io
import json

import scripts.privacy_preflight as preflight


def run_preflight(monkeypatch, capsys, text):
    monkeypatch.setattr("sys.stdin", io.StringIO(text))
    exit_code = preflight.main()
    output = capsys.readouterr().out
    return exit_code, json.loads(output), output


def test_preflight_blocks_sensitive_content_without_echoing_values(monkeypatch, capsys):
    private_text = "Contacto: persona-secreta@example.com"
    exit_code, result, output = run_preflight(monkeypatch, capsys, private_text)

    assert exit_code == 2
    assert result["status"] == "blocked"
    assert "identificador_directo" in result["categories"]
    assert private_text not in output
    assert "persona-secreta@example.com" not in output


def test_preflight_does_not_authorize_general_text(monkeypatch, capsys):
    exit_code, result, _ = run_preflight(
        monkeypatch,
        capsys,
        "Quiero investigar cómo se construyen las decisiones.",
    )

    assert exit_code != 0
    assert result["status"] == "blocked"
    assert result["categories"] == []
    assert "no demuestra" in result["notice"]


def test_preflight_blocks_empty_input(monkeypatch, capsys):
    exit_code, result, _ = run_preflight(monkeypatch, capsys, "  ")

    assert exit_code == 2
    assert result["status"] == "blocked"
    assert result["risk"] == "unknown"


def test_preflight_fails_closed_when_detector_raises(monkeypatch, capsys):
    def fail(_text):
        raise RuntimeError("internal failure")

    monkeypatch.setattr(preflight, "detect_sensitive_content", fail)
    exit_code, result, output = run_preflight(monkeypatch, capsys, "texto sintético")

    assert exit_code != 0
    assert result["status"] == "blocked"
    assert result["risk"] == "unknown"
    assert "privacy_check_failed" in result["categories"]
    assert "internal failure" not in output
