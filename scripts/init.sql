-- SemLoop PostgreSQL initialization script

-- Create events table with JSONB and vector columns
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    agent VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL,
    meta JSONB,
    embedding vector(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
CREATE INDEX IF NOT EXISTS idx_events_agent ON events(agent);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_payload ON events USING GIN(payload);
CREATE INDEX IF NOT EXISTS idx_events_meta ON events USING GIN(meta);

-- Create index for vector similarity search (IVFFlat)
-- Note: This requires data before building, so we create it empty initially
CREATE INDEX IF NOT EXISTS idx_events_embedding ON events 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create session summaries table
CREATE TABLE IF NOT EXISTS session_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    summary JSONB NOT NULL,
    context_hash VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_summaries_session ON session_summaries(session_id);
CREATE INDEX IF NOT EXISTS idx_summaries_timestamp ON session_summaries(timestamp DESC);

-- Create metrics table for time-series data
CREATE TABLE IF NOT EXISTS metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    agent VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value NUMERIC NOT NULL,
    tags JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_agent ON metrics(agent);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name);

-- Hypertable for time-series (if TimescaleDB extension is available)
-- Uncomment if using TimescaleDB:
-- CREATE EXTENSION IF NOT EXISTS timescaledb;
-- SELECT create_hypertable('metrics', 'timestamp', if_not_exists => TRUE);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO semloop;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO semloop;