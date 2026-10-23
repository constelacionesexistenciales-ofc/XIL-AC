-- Archivo Vivo de Conversaciones (AVC): esquema inicial versionado.
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
