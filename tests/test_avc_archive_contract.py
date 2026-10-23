"""Tests de contrato AVC sin conexión ni datos reales."""

from datetime import datetime, timezone
from hashlib import sha256
from uuid import uuid4

import pytest

from core.avc_archive import (
    AVCError,
    ConversationRecord,
    RawMessage,
    SCHEMA_SQL,
    _complete_sequence,
    _manifest_hash,
    _message_hash,
    save_conversation,
)


def test_hash_preserves_exact_unicode_and_newlines():
    message = RawMessage(
        message_id=uuid4(),
        sequence_no=0,
        role="user",
        content_raw="¿Qué reconocés?\r\n  acción 🧭 ",
    )
    expected = sha256(message.content_raw.encode("utf-8")).hexdigest()
    assert _message_hash(message) == expected


def test_empty_message_is_a_valid_source_message():
    message = RawMessage(
        message_id=uuid4(),
        sequence_no=0,
        role="assistant",
        content_raw="",
    )
    assert _message_hash(message) == sha256(b"").hexdigest()


def test_whitespace_changes_hash():
    first = RawMessage(
        message_id=uuid4(),
        sequence_no=0,
        role="user",
        content_raw="texto",
    )
    second = RawMessage(
        message_id=uuid4(),
        sequence_no=0,
        role="user",
        content_raw=" texto ",
    )
    assert _message_hash(first) != _message_hash(second)


@pytest.mark.parametrize(
    ("expected", "sequences", "complete"),
    [
        (3, [0, 1, 2], True),
        (3, [0, 2], False),
        (2, [0, 1, 2], False),
        (2, [1, 0], False),
        (None, [0, 1], False),
        (0, [], True),
    ],
)
def test_sequence_coverage_requires_exact_zero_based_sequence(
    expected,
    sequences,
    complete,
):
    assert _complete_sequence(expected, sequences) is complete


def _manifest_fixture(content="texto original"):
    conversation = {
        "conversation_id": uuid4(),
        "source_system": "synthetic-test",
        "source_conversation_id": "source-1",
        "title": "Conversación sintética",
        "expected_message_count": 1,
        "metadata": {"export_version": 1},
    }
    message = {
        "message_id": uuid4(),
        "sequence_no": 0,
        "role": "user",
        "content_raw": content,
        "source_message_id": "message-1",
        "source_created_at": datetime(2026, 10, 23, tzinfo=timezone.utc),
        "metadata": {"synthetic": True},
    }
    return conversation, [message]


def test_manifest_hash_is_deterministic():
    conversation, messages = _manifest_fixture()
    first = _manifest_hash(conversation, messages)
    second = _manifest_hash(conversation, messages)
    assert first == second


def test_manifest_hash_changes_when_source_content_changes():
    conversation, messages = _manifest_fixture()
    original = _manifest_hash(conversation, messages)
    changed = [dict(messages[0], content_raw="contenido modificado")]
    assert _manifest_hash(conversation, changed) != original


def test_schema_does_not_delete_messages_cascading_from_conversation():
    assert "ON DELETE CASCADE" not in SCHEMA_SQL.upper()


def test_save_rejects_out_of_order_messages_before_database_access(monkeypatch):
    def fail_if_database_is_used():
        pytest.fail("Database must not be accessed for invalid input")

    monkeypatch.setattr("core.avc_archive.connection", fail_if_database_is_used)
    record = ConversationRecord(
        conversation_id=uuid4(),
        source_system="synthetic-test",
        source_conversation_id="source-1",
        title=None,
        capture_status="PARTIAL",
        expected_message_count=3,
    )
    messages = [
        RawMessage(uuid4(), 2, "assistant", "second"),
        RawMessage(uuid4(), 0, "user", "first"),
    ]
    with pytest.raises(AVCError, match="source order"):
        save_conversation(record, messages)
