"""Tests de contrato AVC sin conexión ni datos reales."""
from hashlib import sha256
from uuid import uuid4

from core.avc_archive import RawMessage, _message_hash


def test_hash_preserves_exact_unicode_and_newlines():
    message = RawMessage(
        message_id=uuid4(), sequence_no=0, role="user",
        content_raw="¿Qué reconocés?\r\n  acción 🧭 ",
    )
    assert _message_hash(message) == sha256(message.content_raw.encode("utf-8")).hexdigest()


def test_empty_message_is_a_valid_source_message():
    message = RawMessage(message_id=uuid4(), sequence_no=0, role="assistant", content_raw="")
    assert _message_hash(message) == sha256(b"").hexdigest()


def test_whitespace_changes_hash():
    a = RawMessage(message_id=uuid4(), sequence_no=0, role="user", content_raw="texto")
    b = RawMessage(message_id=uuid4(), sequence_no=0, role="user", content_raw=" texto ")
    assert _message_hash(a) != _message_hash(b)
