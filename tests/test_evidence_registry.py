from core.evidence_registry import (
    EvidenceRecord,
    ResearchClaim,
    ResearchReport,
    abstention_claim,
)


def evidence(evidence_id="e1"):
    return EvidenceRecord(
        evidence_id=evidence_id,
        url="https://example.org/source",
        title="Source title",
        publisher="Example publisher",
        retrieved_at="2026-10-11T00:00:00+00:00",
    )


def test_supported_claim_requires_known_evidence():
    report = ResearchReport(
        execution_id="exec-1",
        question="What is known?",
        evidence=[evidence()],
        claims=[ResearchClaim("c1", "A sourced statement.", ("e1",), 0.8, "supported")],
    )
    assert report.validate() == []
    assert report.is_publishable()


def test_claim_with_unknown_evidence_fails_closed():
    report = ResearchReport(
        execution_id="exec-2",
        question="What is known?",
        evidence=[evidence()],
        claims=[ResearchClaim("c1", "A statement.", ("missing",), 0.5)],
    )
    assert "claim:c1:unknown_evidence:missing" in report.validate()
    assert not report.is_publishable()


def test_claim_without_evidence_is_not_publishable():
    report = ResearchReport(
        execution_id="exec-3",
        question="What is known?",
        claims=[ResearchClaim("c1", "Unsupported statement.")],
    )
    assert "claim:c1:claim_requires_evidence_or_explicit_abstention" in report.validate()
    assert not report.is_publishable()


def test_explicit_abstention_is_valid_and_publishable():
    report = ResearchReport(
        execution_id="exec-4",
        question="What is known?",
        claims=[abstention_claim("c1", "No reliable sources were retrieved.")],
        limitations=["Search was unavailable."],
    )
    assert report.validate() == []
    assert report.is_publishable()


def test_invalid_source_url_is_rejected():
    item = EvidenceRecord("e1", "javascript:alert(1)", "Title", "Publisher", "2026-10-11")
    assert "valid_http_url_required" in item.validate()


def test_duplicate_evidence_ids_are_rejected():
    report = ResearchReport(
        execution_id="exec-5",
        question="Question",
        evidence=[evidence(), evidence()],
        claims=[ResearchClaim("c1", "Statement.", ("e1",))],
    )
    assert "duplicate_evidence_id" in report.validate()


def test_disputed_claim_requires_caveat():
    report = ResearchReport(
        execution_id="exec-6",
        question="Question",
        evidence=[evidence()],
        claims=[ResearchClaim("c1", "Conflicting statement.", ("e1",), 0.4, "disputed")],
    )
    assert not report.is_publishable()



import pytest


@pytest.mark.parametrize(
    "url",
    [
        "http://example.org/source",
        "https://user:password@example.org/source",
        "https://example.org:8443/source",
        "https://localhost/admin",
        "https://service.local/path",
        "https://127.0.0.1/admin",
        "https://192.168.1.10/admin",
        "https://[::1]/admin",
        "https://example.org/has space",
        "https://example.org/" + "x" * 2050,
        "https://example.org:invalid/path",
    ],
)
def test_evidence_rejects_unsafe_source_urls(url):
    item = EvidenceRecord("e1", url, "Title", "Publisher", "2026-10-11")
    assert item.validate()
    assert not ResearchReport(
        execution_id="exec-unsafe",
        question="Question",
        evidence=[item],
        claims=[ResearchClaim("c1", "Statement.", ("e1",))],
    ).is_publishable()


def test_evidence_accepts_public_https_source():
    item = EvidenceRecord(
        "e1", "https://example.org/source", "Title", "Publisher", "2026-10-11"
    )
    assert item.validate() == []
