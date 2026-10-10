-- Esquema inicial mínimo para trazabilidad técnica sin almacenar transcripciones.
CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    execution_id UUID NOT NULL,
    event_type TEXT NOT NULL CHECK (length(event_type) BETWEEN 1 AND 100),
    actor_id TEXT,
    outcome TEXT NOT NULL CHECK (length(outcome) BETWEEN 1 AND 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS audit_events_execution_id_idx ON audit_events(execution_id);
CREATE INDEX IF NOT EXISTS audit_events_created_at_idx ON audit_events(created_at);
