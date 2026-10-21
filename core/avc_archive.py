"""Archivo Vivo de Conversaciones (AVC): almacenamiento fuente, íntegro y recuperable.

Este módulo no llama a modelos ni transmite contenido a proveedores externos.
Las tablas se crean mediante initialize_schema() durante una migración controlada.
No registra contenido de mensajes en logs. Las filas originales son append-only a nivel
de esta API; la inmutabilidad real también debe imponerse con permisos/trigger SQL.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Iterable
from uuid import UUID

from core.db import connection


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS avc_conversations (
    conversation_id UUID PRIMARY KEY,
    source_system TEXT NOT NULL,
    source_conversation_id TEXT,
    title TEXT,
    capture_status TEXT NOT NULL CHECK (capture_status IN
        ('VERIFIED', 'PARTIAL', 'MISSING', 'IMPORT_FAILED')),
    expected_message_count INTEGER CHECK (expected_message_count IS NULL OR expected_message_count >= 0),
    imported_message_count INTEGER NOT NULL DEFAULT 0 CHECK (imported_message_count >= 0),
    manifest_sha256 CHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS avc_messages (
    message_id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES avc_conversations(conversation_id) ON DELETE CASCADE,
    sequence_no INTEGER NOT NULL CHECK (sequence_no >= 0),
    role TEXT NOT NULL,
    content_raw TEXT NOT NULL,
    source_message_id TEXT,
    source_created_at TIMESTAMPTZ,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    content_sha256 CHAR(64) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (conversation_id, sequence_no),
    UNIQUE (conversation_id, source_message_id)
);
CREATE INDEX IF NOT EXISTS avc_messages_conversation_order_idx
    ON avc_messages (conversation_id, sequence_no);
CREATE INDEX IF NOT EXISTS avc_conversations_source_idx
    ON avc_conversations (source_system, source_conversation_id);
"""


class AVCError(RuntimeError):
    """Error AVC sin incluir texto fuente ni datos personales."""


@dataclass(frozen=True)
class RawMessage:
    message_id: UUID
    sequence_no: int
    role: str
    content_raw: str
    source_message_id: str | None = None
    source_created_at: datetime | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ConversationRecord:
    conversation_id: UUID
    source_system: str
    source_conversation_id: str | None
    title: str | None
    capture_status: str
    expected_message_count: int | None
    metadata: dict[str, Any] | None = None


def initialize_schema() -> None:
    """Apply idempotent DDL explicitly during a controlled migration/deployment step."""
    with connection() as conn:
        conn.execute(SCHEMA_SQL)


def _message_hash(message: RawMessage) -> str:
    # Hash the exact UTF-8 text; no normalization, trimming, or newline rewriting.
    return sha256(message.content_raw.encode("utf-8")).hexdigest()


def save_conversation(record: ConversationRecord, messages: Iterable[RawMessage]) -> int:
    """Save a conversation and its messages atomically; repeated identical imports are idempotent.

    If an existing message ID/sequence points to different source content, abort rather
    than overwrite source evidence. Callers must supply messages in their source order.
    """
    batch = list(messages)
    if not record.source_system.strip():
        raise AVCError("source_system is required")
    if record.capture_status not in {"VERIFIED", "PARTIAL", "MISSING", "IMPORT_FAILED"}:
        raise AVCError("invalid capture status")
    if len({m.sequence_no for m in batch}) != len(batch):
        raise AVCError("duplicate sequence numbers")
    if any(m.sequence_no < 0 or not m.role.strip() for m in batch):
        raise AVCError("invalid message envelope")
    if record.expected_message_count is not None and len(batch) > record.expected_message_count:
        raise AVCError("import exceeds declared message count")

    with connection() as conn:
        conn.execute(
            """INSERT INTO avc_conversations
               (conversation_id, source_system, source_conversation_id, title,
                capture_status, expected_message_count, imported_message_count, metadata)
               VALUES (%s,%s,%s,%s,%s,%s,0,%s::jsonb)
               ON CONFLICT (conversation_id) DO NOTHING""",
            (record.conversation_id, record.source_system, record.source_conversation_id,
             record.title, record.capture_status, record.expected_message_count,
             _json(record.metadata)),
        )
        existing = conn.execute(
            """SELECT source_system, source_conversation_id FROM avc_conversations
               WHERE conversation_id=%s""", (record.conversation_id,)
        ).fetchone()
        if not existing or existing[0] != record.source_system or existing[1] != record.source_conversation_id:
            raise AVCError("conversation identity conflict")

        for msg in batch:
            digest = _message_hash(msg)
            conn.execute(
                """INSERT INTO avc_messages
                   (message_id, conversation_id, sequence_no, role, content_raw,
                    source_message_id, source_created_at, content_sha256, metadata)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                   ON CONFLICT DO NOTHING""",
                (msg.message_id, record.conversation_id, msg.sequence_no, msg.role,
                 msg.content_raw, msg.source_message_id, msg.source_created_at,
                 digest, _json(msg.metadata)),
            )
            by_id = conn.execute(
                """SELECT conversation_id, sequence_no, role, content_raw, content_sha256
                   FROM avc_messages WHERE message_id=%s""", (msg.message_id,)
            ).fetchone()
            by_seq = conn.execute(
                """SELECT message_id, role, content_raw, content_sha256
                   FROM avc_messages WHERE conversation_id=%s AND sequence_no=%s""",
                (record.conversation_id, msg.sequence_no),
            ).fetchone()
            expected = (record.conversation_id, msg.sequence_no, msg.role, msg.content_raw, digest)
            if by_id != expected or not by_seq or by_seq[1:] != (msg.role, msg.content_raw, digest):
                raise AVCError("source conflict; existing records were not overwritten")

        count = conn.execute(
            "SELECT count(*) FROM avc_messages WHERE conversation_id=%s",
            (record.conversation_id,),
        ).fetchone()[0]
        final_status = record.capture_status
        if record.expected_message_count is not None and count != record.expected_message_count:
            final_status = "PARTIAL"
        conn.execute(
            """UPDATE avc_conversations
               SET imported_message_count=%s, capture_status=%s, captured_at=now()
               WHERE conversation_id=%s""",
            (count, final_status, record.conversation_id),
        )
        return count


def retrieve_conversation(conversation_id: UUID) -> dict[str, Any]:
    """Return exact stored text in source order plus integrity verification."""
    with connection() as conn:
        header = conn.execute(
            """SELECT conversation_id, source_system, source_conversation_id, title,
                      capture_status, expected_message_count, imported_message_count,
                      manifest_sha256, metadata
               FROM avc_conversations WHERE conversation_id=%s""", (conversation_id,)
        ).fetchone()
        if not header:
            raise AVCError("conversation not found")
        rows = conn.execute(
            """SELECT message_id, sequence_no, role, content_raw, source_message_id,
                      source_created_at, captured_at, content_sha256, metadata
               FROM avc_messages WHERE conversation_id=%s ORDER BY sequence_no""",
            (conversation_id,),
        ).fetchall()

    messages = []
    all_valid = True
    for row in rows:
        digest = sha256(row[3].encode("utf-8")).hexdigest()
        valid = digest == row[7].strip()
        all_valid = all_valid and valid
        messages.append({
            "message_id": str(row[0]), "sequence_no": row[1], "role": row[2],
            "content_raw": row[3], "source_message_id": row[4],
            "source_created_at": row[5].isoformat() if row[5] else None,
            "captured_at": row[6].isoformat(), "content_sha256": row[7].strip(),
            "integrity_verified": valid, "metadata": row[8],
        })
    expected = header[5]
    complete = expected is not None and expected == len(messages)
    return {
        "conversation": {
            "conversation_id": str(header[0]), "source_system": header[1],
            "source_conversation_id": header[2], "title": header[3],
            "capture_status": header[4], "expected_message_count": expected,
            "imported_message_count": header[6], "manifest_sha256": header[7],
            "metadata": header[8],
        },
        "messages": messages,
        "integrity": {
            "all_message_hashes_valid": all_valid,
            "message_count": len(messages),
            "expected_count_matches": complete,
            "complete": complete and all_valid and header[4] == "VERIFIED",
        },
    }


def _json(value: dict[str, Any] | None) -> str:
    import json
    return json.dumps(value or {}, ensure_ascii=False, separators=(",", ":"))
