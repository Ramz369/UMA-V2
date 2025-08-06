-- Evolution SemLoop PostgreSQL initialization script
-- Separate schema for evolution engine's memory

-- Create evolution-specific schemas
CREATE SCHEMA IF NOT EXISTS evolution;
CREATE SCHEMA IF NOT EXISTS treasury;

-- Set default schema
SET search_path TO evolution, public;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Evolution events table
CREATE TABLE IF NOT EXISTS evolution.events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    agent VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload JSONB NOT NULL,
    meta JSONB,
    embedding vector(1536),
    garbage BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for evolution events
CREATE INDEX IF NOT EXISTS idx_evo_events_type ON evolution.events(type);
CREATE INDEX IF NOT EXISTS idx_evo_events_agent ON evolution.events(agent);
CREATE INDEX IF NOT EXISTS idx_evo_events_timestamp ON evolution.events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_evo_events_payload ON evolution.events USING GIN(payload);
CREATE INDEX IF NOT EXISTS idx_evo_events_meta ON evolution.events USING GIN(meta);
CREATE INDEX IF NOT EXISTS idx_evo_events_garbage ON evolution.events(garbage) WHERE garbage = FALSE;

-- Evolution proposals table
CREATE TABLE IF NOT EXISTS evolution.proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_date DATE NOT NULL DEFAULT CURRENT_DATE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    agent VARCHAR(100) NOT NULL,
    priority VARCHAR(20) CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    estimated_cost NUMERIC(10, 2),
    estimated_revenue NUMERIC(10, 2),
    status VARCHAR(20) DEFAULT 'PENDING',
    decision JSONB,
    implementation_result JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Evolution lineages table
CREATE TABLE IF NOT EXISTS evolution.lineages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    version VARCHAR(20) NOT NULL,
    parent_lineage VARCHAR(100),
    focus VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    terminated_at TIMESTAMPTZ,
    fitness_score NUMERIC(5, 2),
    revenue_generated NUMERIC(10, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- Treasury transactions table
CREATE TABLE IF NOT EXISTS treasury.transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    type VARCHAR(20) CHECK (type IN ('CREDIT', 'DEBIT', 'REVENUE', 'INVESTMENT')),
    amount NUMERIC(10, 2) NOT NULL,
    balance_after NUMERIC(10, 2) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    related_experiment VARCHAR(100),
    metadata JSONB
);

-- Revenue streams table
CREATE TABLE IF NOT EXISTS treasury.revenue_streams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'PLANNED',
    launch_date DATE,
    monthly_revenue NUMERIC(10, 2),
    total_revenue NUMERIC(10, 2) DEFAULT 0,
    customer_count INTEGER DEFAULT 0,
    metadata JSONB
);

-- Evolution metrics table
CREATE TABLE IF NOT EXISTS evolution.metrics (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metric_name VARCHAR(100) NOT NULL,
    value NUMERIC NOT NULL,
    agent VARCHAR(100),
    lineage VARCHAR(100),
    tags JSONB
);

-- Living mode sessions table
CREATE TABLE IF NOT EXISTS evolution.living_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_end TIMESTAMPTZ,
    trigger_reason TEXT,
    decisions_made JSONB,
    transcript TEXT,
    outcome VARCHAR(100)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_proposals_status ON evolution.proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_date ON evolution.proposals(proposal_date DESC);
CREATE INDEX IF NOT EXISTS idx_lineages_active ON evolution.lineages(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_transactions_date ON treasury.transactions(transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_revenue_status ON treasury.revenue_streams(status);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON evolution.metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON evolution.metrics(metric_name);

-- Create summary views
CREATE OR REPLACE VIEW evolution.daily_summary AS
SELECT 
    CURRENT_DATE as summary_date,
    COUNT(DISTINCT p.id) as proposals_today,
    COUNT(DISTINCT CASE WHEN p.status = 'APPROVED' THEN p.id END) as approved_proposals,
    COUNT(DISTINCT l.id) as active_lineages,
    COALESCE(SUM(t.amount) FILTER (WHERE t.type = 'REVENUE'), 0) as revenue_today,
    COALESCE(SUM(t.amount) FILTER (WHERE t.type = 'DEBIT'), 0) as expenses_today,
    MAX(t.balance_after) as current_balance
FROM evolution.proposals p
CROSS JOIN evolution.lineages l
CROSS JOIN treasury.transactions t
WHERE p.proposal_date = CURRENT_DATE
    AND l.is_active = TRUE
    AND t.transaction_date::date = CURRENT_DATE;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA evolution TO evolution;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA treasury TO evolution;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA evolution TO evolution;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA treasury TO evolution;

-- Initial seed data
INSERT INTO treasury.transactions (type, amount, balance_after, description)
VALUES ('CREDIT', 0, 0, 'System initialized - awaiting seed budget');

INSERT INTO evolution.lineages (name, version, focus)
VALUES ('uma-v2', '2.0', 'production_stable');