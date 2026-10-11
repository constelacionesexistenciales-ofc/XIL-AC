import io
import json

from scripts.privacy_preflight import main


def test_preflight_blocks_sensitive_content_without_echoing_values(monkeypatch, capsys):
    private_text = "Contacto: alexis@example.com"
    monkeypatch.setattr("sys.stdin", io.StringIO(private_text))

    exit_code = main()
    output = capsys.readouterr().out

    assert exit_code == 2
    result = json.loads(output)
    assert result["status"] == "blocked"
    assert "identificador_directo" in result["categories"]
    assert private_text not in output
    assert "alexis@example.com" not in output


def test_preflight_allows_general_text_with_caution(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO("Quiero investigar cómo se construyen las decisiones."),
    )

    exit_code = main()
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert result["status"] == "no_signal_detected"
    assert result["categories"] == []
    assert "no garantiza" in result["notice"]


def test_preflight_blocks_empty_input(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("  "))

    exit_code = main()
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert result["risk"] == "unknown"
