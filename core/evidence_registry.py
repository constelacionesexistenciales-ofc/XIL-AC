"""Deterministic evidence registry for traceable research outputs.

This module does not retrieve sources or judge truth. It enforces provenance links
between claims and source records so downstream synthesis can abstain when evidence
is missing. URLs are metadata only; callers must fetch and assess sources separately.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_id: str
    url: str
    title: str
    publisher: str
    retrieved_at: str
    excerpt: str = ""
    source_type: str = "web"
    notes: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.evidence_id.strip():
            errors.append("evidence_id_required")
        parsed = urlparse(self.url)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc:
            errors.append("valid_http_url_required")
        if not self.title.strip():
            errors.append("title_required")
        if not self.publisher.strip():
            errors.append("publisher_required")
        try:
            datetime.fromisoformat(self.retrieved_at.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            errors.append("retrieved_at_must_be_iso8601")
        if self.source_type not in {"web", "paper", "book", "dataset", "official"}:
            errors.append("unsupported_source_type")
        return errors


@dataclass(frozen=True, slots=True)
class ResearchClaim:
    claim_id: str
    text: str
    evidence_ids: tuple[str, ...] = ()
    confidence: float | None = None
    status: str = "provisional"
    caveat: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.claim_id.strip():
            errors.append("claim_id_required")
        if not self.text.strip():
            errors.append("claim_text_required")
        if not self.evidence_ids:
            errors.append("claim_requires_evidence_or_explicit_abstention")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence_must_be_between_0_and_1")
        if self.status not in {"supported", "disputed", "provisional", "abstain"}:
            errors.append("unsupported_claim_status")
        if self.status == "abstain" and not self.caveat.strip():
            errors.append("abstention_requires_reason")
        return errors


@dataclass(slots=True)
class ResearchReport:
    execution_id: str
    question: str
    evidence: list[EvidenceRecord] = field(default_factory=list)
    claims: list[ResearchClaim] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.execution_id.strip():
            errors.append("execution_id_required")
        if not self.question.strip():
            errors.append("research_question_required")
        evidence_ids = [item.evidence_id for item in self.evidence]
        claim_ids = [item.claim_id for item in self.claims]
        if len(evidence_ids) != len(set(evidence_ids)):
            errors.append("duplicate_evidence_id")
        if len(claim_ids) != len(set(claim_ids)):
            errors.append("duplicate_claim_id")
        evidence_set = set(evidence_ids)
        for item in self.evidence:
            errors.extend(f"evidence:{item.evidence_id}:{err}" for err in item.validate())
        for claim in self.claims:
            errors.extend(f"claim:{claim.claim_id}:{err}" for err in claim.validate())
            for evidence_id in claim.evidence_ids:
                if evidence_id not in evidence_set:
                    errors.append(f"claim:{claim.claim_id}:unknown_evidence:{evidence_id}")
        if not self.claims:
            errors.append("report_requires_claim_or_abstention")
        return errors

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation without fetching or altering source URLs."""
        return asdict(self)

    def is_publishable(self) -> bool:
        """Fail closed: structurally valid and no unresolved claims without caveats."""
        if self.validate():
            return False
        return all(
            claim.status != "disputed" or bool(claim.caveat.strip())
            for claim in self.claims
        )


def abstention_claim(claim_id: str, reason: str) -> ResearchClaim:
    """Create an explicit abstention when evidence is insufficient."""
    return ResearchClaim(
        claim_id=claim_id,
        text="No se puede concluir con la evidencia disponible.",
        evidence_ids=(),
        confidence=0.0,
        status="abstain",
        caveat=reason.strip() or "Evidencia insuficiente.",
    )
