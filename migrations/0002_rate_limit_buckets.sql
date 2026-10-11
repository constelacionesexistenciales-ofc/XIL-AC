-- Buckets compartidos entre instancias para limitar solicitudes por actor y ámbito.
-- Se guarda un hash de subject, no el identificador de identidad en esta tabla.
CREATE TABLE IF NOT EXISTS rate_limit_buckets (
    subject_hash CHAR(64) NOT NULL,
    scope TEXT NOT NULL CHECK (length(scope) BETWEEN 1 AND 80),
    bucket_start BIGINT NOT NULL,
    request_count INTEGER NOT NULL CHECK (request_count > 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (subject_hash, scope, bucket_start)
);
CREATE INDEX IF NOT EXISTS rate_limit_buckets_updated_at_idx
    ON rate_limit_buckets(updated_at);
