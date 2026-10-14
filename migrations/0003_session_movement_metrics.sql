-- Datos mínimos; no guardar transcripciones, nombres ni texto libre.
CREATE TABLE IF NOT EXISTS session_movement_sessions (
    session_id UUID PRIMARY KEY,
    actor_id TEXT NOT NULL CHECK (length(actor_id) BETWEEN 1 AND 200),
    objective TEXT NOT NULL CHECK (
        objective IN ('stabilization', 'availability', 'exploration',
                      'integration', 'action', 'other')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    closed_at TIMESTAMPTZ,
    CHECK (closed_at IS NULL OR closed_at >= created_at)
);
CREATE INDEX IF NOT EXISTS session_movement_owner_created_idx
    ON session_movement_sessions(actor_id, created_at DESC);

CREATE TABLE IF NOT EXISTS session_movement_snapshots (
    snapshot_id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES session_movement_sessions(session_id) ON DELETE CASCADE,
    actor_id TEXT NOT NULL CHECK (length(actor_id) BETWEEN 1 AND 200),
    phase TEXT NOT NULL CHECK (phase IN ('arrival', 'during', 'closing')),
    source TEXT NOT NULL CHECK (
        source IN ('consultante_self_report', 'facilitator_observation', 'jointly_reviewed')
    ),
    scores JSONB NOT NULL CHECK (jsonb_typeof(scores) = 'object'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (
        scores ? 'availability' AND scores ? 'action_capacity'
        AND scores ? 'integration_capacity' AND scores ? 'phenomenological_movement'
        AND scores ? 'vitality_energy' AND scores ? 'coping_availability'
    )
);
CREATE INDEX IF NOT EXISTS session_movement_snapshots_session_idx
    ON session_movement_snapshots(session_id, created_at);
