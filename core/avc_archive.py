"""Archivo Vivo de Conversaciones (AVC): almacenamiento fuente, íntegro y recuperable.

Este módulo no llama a modelos ni transmite contenido a proveedores externos.
Las tablas se crean mediante initialize_schema() durante una migración controlada.
No registra contenido de mensajes en logs. Las filas originales son append-only a nivel
de esta API; la inmutabilidad real también debe imponerse con permisos/trigger SQL.
"""
from __future__ import annotations

import json
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
    expected_message_count INTEGER CHECK (
        expected_message_count IS NULL OR expected_message_count >= 0
    ),
    imported_message_count INTEGER NOT NULL DEFAULT 0 CHECK (
        imported_message_count >= 0
    ),
    manifest_sha256 CHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    captured_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS avc_messages (
    message_id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES avc_conversations(conversation_id),
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


def _timestamp_text(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.isoformat()
    return value.astimezone(timezone.utc).isoformat()


def _manifest_hash(
    conversation: dict[str, Any],
    messages: list[dict[str, Any]],
) -> str:
    """Hash a canonical manifest of persisted source fields, not a source completeness claim."""
    payload = {
        "schema_version": 1,
        "conversation": {
            "conversation_id": str(conversation["conversation_id"]),
            "source_system": conversation["source_system"],
            "source_conversation_id": conversation["source_conversation_id"],
            "title": conversation["title"],
            "expected_message_count": conversation["expected_message_count"],
            "metadata": conversation["metadata"] or {},
        },
        "messages": [
            {
                "message_id": str(message["message_id"]),
                "sequence_no": message["sequence_no"],
                "role": message["role"],
                "content_sha256": sha256(
                    message["content_raw"].encode("utf-8")
                ).hexdigest(),
                "source_message_id": message["source_message_id"],
                "source_created_at": _timestamp_text(
                    message["source_created_at"]
                ),
                "metadata": message["metadata"] or {},
            }
            for message in messages
        ],
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def _complete_sequence(
    expected_count: int | None,
    sequence_numbers: list[int],
) -> bool:
    return (
        expected_count is not None
        and sequence_numbers == list(range(expected_count))
    )


def save_conversation(record: ConversationRecord, messages: Iterable[RawMessage]) -> int:
    """Save source messages atomically and idempotently; never overwrite conflicting data.

    A VERIFIED result requires a declared count and a complete zero-based sequence.
    A canonical manifest detects accidental changes but is not a tamper-proof signature.
    """
    batch = list(messages)
    if not record.source_system.strip():
        raise AVCError("source_system is required")
    if record.capture_status not in {"VERIFIED", "PARTIAL", "MISSING", "IMPORT_FAILED"}:
        raise AVCError("invalid capture status")
    if record.expected_message_count is not None and record.expected_message_count < 0:
        raise AVCError("expected_message_count cannot be negative")
    if len({message.message_id for message in batch}) != len(batch):
        raise AVCError("duplicate message IDs")
    if len({message.sequence_no for message in batch}) != len(batch):
        raise AVCError("duplicate sequence numbers")
    if any(message.sequence_no < 0 or not message.role.strip() for message in batch):
        raise AVCError("invalid message envelope")
    sequences = [message.sequence_no for message in batch]
    if sequences != sorted(sequences):
        raise AVCError("messages must be supplied in source order")
    if (
        record.expected_message_count is not None
        and len(batch) > record.expected_message_count
    ):
        raise AVCError("import exceeds declared message count")

    with connection() as conn:
        conn.execute(
            """INSERT INTO avc_conversations
               (conversation_id, source_system, source_conversation_id, title,
                capture_status, expected_message_count, imported_message_count, metadata)
               VALUES (%s,%s,%s,%s,%s,%s,0,%s::jsonb)
               ON CONFLICT (conversation_id) DO NOTHING""",
            (
                record.conversation_id,
                record.source_system,
                record.source_conversation_id,
                record.title,
                record.capture_status,
                record.expected_message_count,
                _json(record.metadata),
            ),
        )
        existing = conn.execute(
            """SELECT source_system, source_conversation_id
               FROM avc_conversations WHERE conversation_id=%s""",
            (record.conversation_id,),
        ).fetchone()
        if (
            not existing
            or existing[0] != record.source_system
            or existing[1] != record.source_conversation_id
        ):
            raise AVCError("conversation identity conflict")

        for message in batch:
            digest = _message_hash(message)
            conn.execute(
                """INSERT INTO avc_messages
                   (message_id, conversation_id, sequence_no, role, content_raw,
                    source_message_id, source_created_at, content_sha256, metadata)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                   ON CONFLICT DO NOTHING""",
                (
                    message.message_id,
                    record.conversation_id,
                    message.sequence_no,
                    message.role,
                    message.content_raw,
                    message.source_message_id,
                    message.source_created_at,
                    digest,
                    _json(message.metadata),
                ),
            )
            by_id = conn.execute(
                """SELECT conversation_id, sequence_no, role, content_raw, content_sha256
                   FROM avc_messages WHERE message_id=%s""",
                (message.message_id,),
            ).fetchone()
            by_sequence = conn.execute(
                """SELECT message_id, role, content_raw, content_sha256
                   FROM avc_messages
                   WHERE conversation_id=%s AND sequence_no=%s""",
                (record.conversation_id, message.sequence_no),
            ).fetchone()
            expected = (
                record.conversation_id,
                message.sequence_no,
                message.role,
                message.content_raw,
                digest,
            )
            if (
                by_id != expected
                or not by_sequence
                or by_sequence[1:] != (message.role, message.content_raw, digest)
            ):
                raise AVCError("source conflict; existing records were not overwritten")

        header = conn.execute(
            """SELECT conversation_id, source_system, source_conversation_id, title,
                      expected_message_count, metadata
               FROM avc_conversations WHERE conversation_id=%s""",
            (record.conversation_id,),
        ).fetchone()
        stored_rows = conn.execute(
            """SELECT message_id, sequence_no, role, content_raw, source_message_id,
                      source_created_at, metadata
               FROM avc_messages WHERE conversation_id=%s ORDER BY sequence_no""",
            (record.conversation_id,),
        ).fetchall()
        manifest_conversation = {
            "conversation_id": header[0],
            "source_system": header[1],
            "source_conversation_id": header[2],
            "title": header[3],
            "expected_message_count": header[4],
            "metadata": header[5],
        }
        manifest_messages = [
            {
                "message_id": row[0],
                "sequence_no": row[1],
                "role": row[2],
                "content_raw": row[3],
                "source_message_id": row[4],
                "source_created_at": row[5],
                "metadata": row[6],
            }
            for row in stored_rows
        ]
        count = len(stored_rows)
        stored_sequences = [row[1] for row in stored_rows]
        coverage_complete = (
            count == record.expected_message_count
            and _complete_sequence(record.expected_message_count, stored_sequences)
        )
        final_status = record.capture_status
        if final_status == "VERIFIED" and not coverage_complete:
            final_status = "PARTIAL"
        manifest_digest = _manifest_hash(
            manifest_conversation,
            manifest_messages,
        )
        conn.execute(
            """UPDATE avc_conversations
               SET imported_message_count=%s, capture_status=%s, manifest_sha256=%s
               WHERE conversation_id=%s""",
            (count, final_status, manifest_digest, record.conversation_id),
        )
        return count


def retrieve_conversation(conversation_id: UUID) -> dict[str, Any]:
    """Return exact stored text in source order plus integrity verification."""
    with connection() as conn:
        header = conn.execute(
            """SELECT conversation_id, source_system, source_conversation_id, title,
                      capture_status, expected_message_count, imported_message_count,
                      manifest_sha256, metadata
               FROM avc_conversations WHERE conversation_id=%s""",
            (conversation_id,),
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
    manifest_messages = []
    all_valid = True
    for row in rows:
        digest = sha256(row[3].encode("utf-8")).hexdigest()
        valid = digest == row[7].strip()
        all_valid = all_valid and valid
        messages.append(
            {
                "message_id": str(row[0]),
                "sequence_no": row[1],
                "role": row[2],
                "content_raw": row[3],
                "source_message_id": row[4],
                "source_created_at": row[5].isoformat() if row[5] else None,
                "captured_at": row[6].isoformat(),
                "content_sha256": row[7].strip(),
                "integrity_verified": valid,
                "metadata": row[8],
            }
        )
        manifest_messages.append(
            {
                "message_id": row[0],
                "sequence_no": row[1],
                "role": row[2],
                "content_raw": row[3],
                "source_message_id": row[4],
                "source_created_at": row[5],
                "metadata": row[8],
            }
        )

    expected = header[5]
    sequence_numbers = [message["sequence_no"] for message in messages]
    expected_count_matches = (
        expected is not None and expected == len(messages)
    )
    imported_count_matches = header[6] == len(messages)
    sequence_complete = _complete_sequence(expected, sequence_numbers)
    manifest_conversation = {
        "conversation_id": header[0],
        "source_system": header[1],
        "source_conversation_id": header[2],
        "title": header[3],
        "expected_message_count": expected,
        "metadata": header[8],
    }
    calculated_manifest = _manifest_hash(
        manifest_conversation,
        manifest_messages,
    )
    manifest_valid = (
        header[7] is not None
        and calculated_manifest == header[7].strip()
    )
    complete = (
        expected_count_matches
        and imported_count_matches
        and sequence_complete
        and all_valid
        and manifest_valid
        and header[4] == "VERIFIED"
    )
    return {
        "conversation": {
            "conversation_id": str(header[0]),
            "source_system": header[1],
            "source_conversation_id": header[2],
            "title": header[3],
            "capture_status": header[4],
            "expected_message_count": expected,
            "imported_message_count": header[6],
            "manifest_sha256": header[7],
            "metadata": header[8],
        },
        "messages": messages,
        "integrity": {
            "all_message_hashes_valid": all_valid,
            "message_count": len(messages),
            "expected_count_matches": expected_count_matches,
            "imported_count_matches": imported_count_matches,
            "sequence_complete": sequence_complete,
            "manifest_valid": manifest_valid,
            "complete": complete,
        },
    }


def _json(value: dict[str, Any] | None) -> str:
    return json.dumps(
        value or {},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
