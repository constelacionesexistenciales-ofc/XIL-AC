import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from core.privacy_detector import detect_sensitive_content

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "privacy_parity_cases.json"
HTML_PATH = ROOT / "local-privacy-review" / "index.html"


def _load_desktop_engine():
    path = ROOT / "desktop-gateway" / "privacy_engine.py"
    spec = importlib.util.spec_from_file_location("xilac_desktop_privacy_engine", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DESKTOP_ENGINE = _load_desktop_engine()
CASES = json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
def test_python_detectors_share_risk_and_synthetic_case_contract(case):
    core = detect_sensitive_content(case["text"])
    desktop = DESKTOP_ENGINE.review_text(case["text"])

    assert core.risk == case["risk"]
    assert sorted(core.categories) == sorted(case["core_categories"])
    assert desktop.risk == case["risk"]
    assert sorted(desktop.categories) == sorted(case["desktop_labels"])
    assert desktop.decision == case["desktop_decision"]
    assert case["text"] not in repr(core)
    assert case["text"] not in repr(desktop)


NODE_HARNESS = r"""
const fs = require("node:fs");
const vm = require("node:vm");
const payload = JSON.parse(fs.readFileSync(0, "utf8"));
const match = payload.html.match(/<script>([\s\S]*?)<\/script>/);
if (!match) throw new Error("Inline privacy-review script not found");

function element(tagName = "div") {
  return {
    tagName: tagName.toUpperCase(),
    value: "",
    hidden: false,
    className: "",
    textContent: "",
    children: [],
    listeners: {},
    addEventListener(name, callback) { this.listeners[name] = callback; },
    replaceChildren(...items) { this.children = [...items]; this.textContent = ""; },
    append(...items) { this.children.push(...items); },
    focus() {}
  };
}

const elements = {
  source: element("textarea"),
  result: element("div"),
  scan: element("button"),
  clear: element("button")
};
const document = {
  getElementById(id) { return elements[id]; },
  createElement(tagName) { return element(tagName); }
};
vm.runInNewContext(match[1], { document });

function labels() {
  return elements.result.children
    .filter(child => child.tagName === "UL")
    .flatMap(list => list.children.map(item => item.textContent))
    .sort();
}

const output = payload.cases.map(testCase => {
  elements.source.value = testCase.text;
  elements.result.hidden = true;
  elements.result.className = "";
  elements.result.replaceChildren();
  elements.scan.listeners.click();
  return { id: testCase.id, className: elements.result.className, labels: labels() };
});
process.stdout.write(JSON.stringify(output));
"""


def test_html_detector_matches_shared_risk_corpus_and_never_sends():
    if shutil.which("node") is None:
        pytest.skip("Node.js is unavailable; HTML runtime parity requires Node.js.")

    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    html = HTML_PATH.read_text(encoding="utf-8")
    payload = {
        "html": html,
        "cases": [{"id": case["id"], "text": case["text"]} for case in fixture["cases"]],
    }
    completed = subprocess.run(
        ["node", "-e", NODE_HARNESS],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    assert completed.returncode == 0, completed.stderr
    observed = {item["id"]: item for item in json.loads(completed.stdout)}

    for case in fixture["cases"]:
        assert observed[case["id"]]["className"] == case["html_class"]
        assert observed[case["id"]]["labels"] == sorted(case["html_labels"])


def test_html_review_keeps_network_and_persistent_storage_disabled():
    html = HTML_PATH.read_text(encoding="utf-8")
    assert "connect-src 'none'" in html
    script = html.split("<script>", 1)[1].split("</script>", 1)[0]
    forbidden_apis = (
        "fetch(",
        "XMLHttpRequest",
        "WebSocket",
        "sendBeacon",
        "localStorage",
        "sessionStorage",
        "indexedDB",
    )
    for api in forbidden_apis:
        assert api not in script
