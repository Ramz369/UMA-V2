-- Migration 002: Karmic Ledger (Balance Layer)
-- Part of the Aether Protocol Implementation
-- Sprint 2: Foundation of Balance

-- Create karmic ledger table
CREATE TABLE IF NOT EXISTS evolution.karmic_ledger (
    karma_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    intent_id UUID REFERENCES evolution.intent_graph(intent_id),
    
    -- Karmic accounting
    karma_generated FLOAT NOT NULL,
    karma_balanced FLOAT DEFAULT 0.0,
    karma_debt FLOAT GENERATED ALWAYS AS (karma_generated - karma_balanced) STORED,
    
    -- Balancing mechanisms
    balancing_events UUID[],
    interest_rate FLOAT DEFAULT 0.01,
    accumulated_interest FLOAT DEFAULT 0.0,
    
    -- Cycles
    cycle_number INTEGER DEFAULT 1,
    cycle_completion FLOAT DEFAULT 0.0 CHECK (cycle_completion BETWEEN 0 AND 1),
    
    -- Metadata
    action_details JSONB DEFAULT '{}',
    tags TEXT[],
    
    -- Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    balanced_at TIMESTAMPTZ,
    last_interest_update TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX idx_karma_actor ON evolution.karmic_ledger(actor);
CREATE INDEX idx_karma_debt ON evolution.karmic_ledger(karma_debt) WHERE karma_debt != 0;
CREATE INDEX idx_karma_intent ON evolution.karmic_ledger(intent_id);
CREATE INDEX idx_karma_unbalanced ON evolution.karmic_ledger(balanced_at) WHERE balanced_at IS NULL;
CREATE INDEX idx_karma_cycle ON evolution.karmic_ledger(cycle_number, cycle_completion);

-- Karmic action types table (reference data)
CREATE TABLE IF NOT EXISTS evolution.karma_action_types (
    action_type VARCHAR(50) PRIMARY KEY,
    base_karma FLOAT NOT NULL,
    category VARCHAR(20) CHECK (category IN ('constructive', 'destructive', 'neutral')),
    description TEXT
);

-- Insert standard action types
INSERT INTO evolution.karma_action_types (action_type, base_karma, category, description) VALUES
    -- Constructive actions (positive karma)
    ('refactor', 0.5, 'constructive', 'Code refactoring and cleanup'),
    ('test_creation', 0.4, 'constructive', 'Creating new tests'),
    ('documentation', 0.3, 'constructive', 'Writing documentation'),
    ('optimization', 0.6, 'constructive', 'Performance optimization'),
    ('bug_fix', 0.7, 'constructive', 'Fixing bugs'),
    ('feature_complete', 0.8, 'constructive', 'Completing a feature'),
    ('security_fix', 0.9, 'constructive', 'Fixing security issues'),
    
    -- Destructive actions (negative karma)
    ('quick_fix', -0.3, 'destructive', 'Quick fixes without proper solution'),
    ('hack', -0.5, 'destructive', 'Hacky workarounds'),
    ('test_skip', -0.4, 'destructive', 'Skipping tests'),
    ('debt_creation', -0.6, 'destructive', 'Creating technical debt'),
    ('breaking_change', -0.7, 'destructive', 'Breaking existing functionality'),
    ('security_vulnerability', -0.9, 'destructive', 'Introducing security issues'),
    
    -- Neutral actions
    ('analysis', 0.1, 'neutral', 'Code analysis'),
    ('planning', 0.1, 'neutral', 'Planning tasks'),
    ('review', 0.2, 'neutral', 'Code review')
ON CONFLICT (action_type) DO NOTHING;

-- Karmic balance summary view
CREATE OR REPLACE VIEW evolution.karmic_balance_summary AS
SELECT 
    actor,
    COUNT(*) as total_actions,
    SUM(CASE WHEN karma_generated > 0 THEN karma_generated ELSE 0 END) as positive_karma,
    SUM(CASE WHEN karma_generated < 0 THEN ABS(karma_generated) ELSE 0 END) as negative_karma,
    SUM(karma_debt) as total_debt,
    SUM(accumulated_interest) as total_interest,
    AVG(cycle_completion) as avg_cycle_completion,
    MAX(created_at) as last_action,
    COUNT(CASE WHEN balanced_at IS NOT NULL THEN 1 END) as balanced_actions
FROM evolution.karmic_ledger
GROUP BY actor
ORDER BY total_debt DESC;

-- Function to calculate karmic interest
CREATE OR REPLACE FUNCTION evolution.calculate_karmic_interest()
RETURNS TRIGGER AS $$
DECLARE
    days_passed FLOAT;
    new_interest FLOAT;
BEGIN
    -- Only calculate for unbalanced karma
    IF NEW.balanced_at IS NULL AND NEW.karma_debt != 0 THEN
        -- Calculate days since last update
        days_passed := EXTRACT(EPOCH FROM (NOW() - COALESCE(NEW.last_interest_update, NEW.created_at))) / 86400;
        
        -- Compound interest calculation
        -- Negative karma (debt) accumulates interest
        IF NEW.karma_debt > 0 THEN
            new_interest := NEW.karma_debt * NEW.interest_rate * days_passed;
            NEW.accumulated_interest := NEW.accumulated_interest + new_interest;
            NEW.karma_generated := NEW.karma_generated + new_interest; -- Debt grows
        END IF;
        
        NEW.last_interest_update := NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for interest calculation
CREATE TRIGGER trg_karmic_interest
BEFORE UPDATE ON evolution.karmic_ledger
FOR EACH ROW
EXECUTE FUNCTION evolution.calculate_karmic_interest();

-- Function to find balancing actions
CREATE OR REPLACE FUNCTION evolution.suggest_balancing_actions(
    p_actor VARCHAR(100),
    p_limit INTEGER DEFAULT 5
) RETURNS TABLE(
    action_type VARCHAR(50),
    expected_karma FLOAT,
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        kat.action_type,
        kat.base_karma,
        kat.description
    FROM evolution.karma_action_types kat
    WHERE kat.base_karma > 0  -- Only positive actions for balancing
    AND kat.action_type NOT IN (
        -- Exclude recently performed actions
        SELECT kl.action_type 
        FROM evolution.karmic_ledger kl
        WHERE kl.actor = p_actor
        AND kl.created_at > NOW() - INTERVAL '1 day'
    )
    ORDER BY kat.base_karma DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to balance karma
CREATE OR REPLACE FUNCTION evolution.balance_karma(
    p_karma_id UUID,
    p_balancing_karma_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    v_debt FLOAT;
    v_balance FLOAT;
    v_result BOOLEAN := FALSE;
BEGIN
    -- Get the debt amount
    SELECT karma_debt INTO v_debt
    FROM evolution.karmic_ledger
    WHERE karma_id = p_karma_id;
    
    -- Get the balancing amount
    SELECT ABS(karma_generated) INTO v_balance
    FROM evolution.karmic_ledger
    WHERE karma_id = p_balancing_karma_id
    AND karma_generated > 0;  -- Must be positive karma
    
    IF v_debt IS NOT NULL AND v_balance IS NOT NULL THEN
        -- Update the debt record
        UPDATE evolution.karmic_ledger
        SET karma_balanced = karma_balanced + LEAST(v_debt, v_balance),
            balancing_events = array_append(balancing_events, p_balancing_karma_id),
            balanced_at = CASE 
                WHEN karma_balanced + LEAST(v_debt, v_balance) >= karma_generated 
                THEN NOW() 
                ELSE NULL 
            END
        WHERE karma_id = p_karma_id;
        
        v_result := TRUE;
    END IF;
    
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- Karmic cycle view
CREATE OR REPLACE VIEW evolution.karmic_cycles AS
WITH cycle_stats AS (
    SELECT 
        cycle_number,
        COUNT(*) as actions_in_cycle,
        AVG(karma_generated) as avg_karma,
        SUM(CASE WHEN karma_generated > 0 THEN 1 ELSE 0 END) as positive_actions,
        SUM(CASE WHEN karma_generated < 0 THEN 1 ELSE 0 END) as negative_actions,
        AVG(cycle_completion) as avg_completion
    FROM evolution.karmic_ledger
    GROUP BY cycle_number
)
SELECT 
    cycle_number,
    actions_in_cycle,
    avg_karma,
    positive_actions,
    negative_actions,
    avg_completion,
    CASE 
        WHEN avg_karma > 0.5 THEN 'ASCENDING'
        WHEN avg_karma > 0 THEN 'IMPROVING'
        WHEN avg_karma > -0.5 THEN 'DECLINING'
        ELSE 'DESCENDING'
    END as cycle_trend
FROM cycle_stats
ORDER BY cycle_number DESC;

-- Sample karma entry for testing
INSERT INTO evolution.karmic_ledger (
    actor,
    action_type,
    karma_generated,
    action_details
) VALUES (
    'SYSTEM',
    'refactor',
    0.5,
    '{"description": "Initial karma ledger setup", "impact": "high"}'
);

COMMENT ON TABLE evolution.karmic_ledger IS 'The balance substrate of the Aether Protocol - tracks karmic debt and credit';
COMMENT ON COLUMN evolution.karmic_ledger.karma_debt IS 'Automatically calculated debt (generated - balanced)';
COMMENT ON COLUMN evolution.karmic_ledger.interest_rate IS 'Daily interest rate on unbalanced karma';
COMMENT ON COLUMN evolution.karmic_ledger.cycle_completion IS 'Progress through current karmic cycle (0=start, 1=complete)';