-- Migration 001: Intent Substrate (Consciousness Layer)
-- Part of the Aether Protocol Implementation
-- Sprint 0: Foundation of Consciousness

-- Create evolution schema if not exists
CREATE SCHEMA IF NOT EXISTS evolution;

-- Intent Graph: The consciousness substrate
CREATE TABLE IF NOT EXISTS evolution.intent_graph (
    intent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    intent_type VARCHAR(50) CHECK (intent_type IN ('root', 'branch', 'leaf')),
    description TEXT NOT NULL,
    initiator VARCHAR(100) NOT NULL,
    parent_intent_id UUID REFERENCES evolution.intent_graph(intent_id),
    
    -- Hermetic properties
    polarity FLOAT DEFAULT 0.0 CHECK (polarity BETWEEN -1 AND 1),
    vibration_frequency INTEGER DEFAULT 5 CHECK (vibration_frequency BETWEEN 1 AND 10),
    gestation_phase VARCHAR(20) DEFAULT 'conceived' CHECK (
        gestation_phase IN ('conceived', 'forming', 'manifesting', 'realized', 'transcended')
    ),
    
    -- Tracking
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    fulfilled_at TIMESTAMPTZ,
    total_energy_spent FLOAT DEFAULT 0.0,
    net_value_created FLOAT DEFAULT 0.0,
    
    -- Quantum properties
    coherence_score FLOAT DEFAULT 1.0 CHECK (coherence_score BETWEEN 0 AND 1),
    entanglement_keys TEXT[],
    
    -- Metadata
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for efficient querying
CREATE INDEX idx_intent_parent ON evolution.intent_graph(parent_intent_id);
CREATE INDEX idx_intent_initiator ON evolution.intent_graph(initiator);
CREATE INDEX idx_intent_type ON evolution.intent_graph(intent_type);
CREATE INDEX idx_intent_entanglement ON evolution.intent_graph USING GIN(entanglement_keys);
CREATE INDEX idx_intent_phase ON evolution.intent_graph(gestation_phase);
CREATE INDEX idx_intent_unfulfilled ON evolution.intent_graph(fulfilled_at) WHERE fulfilled_at IS NULL;

-- Intent Lineage View: Track intent hierarchies
CREATE OR REPLACE VIEW evolution.intent_lineage AS
WITH RECURSIVE intent_tree AS (
    -- Root intents
    SELECT 
        intent_id,
        intent_type,
        description,
        initiator,
        parent_intent_id,
        coherence_score,
        0 as depth,
        ARRAY[intent_id] as path
    FROM evolution.intent_graph
    WHERE parent_intent_id IS NULL
    
    UNION ALL
    
    -- Recursive part
    SELECT 
        i.intent_id,
        i.intent_type,
        i.description,
        i.initiator,
        i.parent_intent_id,
        i.coherence_score,
        t.depth + 1,
        t.path || i.intent_id
    FROM evolution.intent_graph i
    INNER JOIN intent_tree t ON i.parent_intent_id = t.intent_id
)
SELECT * FROM intent_tree;

-- Function to calculate intent coherence
CREATE OR REPLACE FUNCTION evolution.calculate_intent_coherence(
    p_intent_id UUID
) RETURNS FLOAT AS $$
DECLARE
    v_coherence FLOAT;
    v_parent_coherence FLOAT;
    v_child_count INT;
    v_fulfilled_children INT;
BEGIN
    -- Get parent coherence
    SELECT coherence_score INTO v_parent_coherence
    FROM evolution.intent_graph
    WHERE intent_id = (
        SELECT parent_intent_id 
        FROM evolution.intent_graph 
        WHERE intent_id = p_intent_id
    );
    
    -- Count children and fulfilled children
    SELECT 
        COUNT(*),
        COUNT(CASE WHEN fulfilled_at IS NOT NULL THEN 1 END)
    INTO v_child_count, v_fulfilled_children
    FROM evolution.intent_graph
    WHERE parent_intent_id = p_intent_id;
    
    -- Calculate coherence
    IF v_child_count = 0 THEN
        -- Leaf node: coherence based on parent
        v_coherence := COALESCE(v_parent_coherence, 1.0);
    ELSE
        -- Branch/root: coherence based on children fulfillment
        v_coherence := (v_fulfilled_children::FLOAT / v_child_count::FLOAT) * 
                      COALESCE(v_parent_coherence, 1.0);
    END IF;
    
    RETURN v_coherence;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update coherence scores
CREATE OR REPLACE FUNCTION evolution.update_intent_coherence()
RETURNS TRIGGER AS $$
BEGIN
    -- Update coherence for the modified intent
    UPDATE evolution.intent_graph
    SET coherence_score = evolution.calculate_intent_coherence(NEW.intent_id)
    WHERE intent_id = NEW.intent_id;
    
    -- Update parent's coherence if exists
    IF NEW.parent_intent_id IS NOT NULL THEN
        UPDATE evolution.intent_graph
        SET coherence_score = evolution.calculate_intent_coherence(NEW.parent_intent_id)
        WHERE intent_id = NEW.parent_intent_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_intent_coherence
AFTER INSERT OR UPDATE OF fulfilled_at ON evolution.intent_graph
FOR EACH ROW
EXECUTE FUNCTION evolution.update_intent_coherence();

-- Sample data for testing
INSERT INTO evolution.intent_graph (
    intent_type, 
    description, 
    initiator,
    vibration_frequency,
    metadata
) VALUES (
    'root',
    'Implement the Aether Protocol to unify COGPLAN consciousness',
    'RAMZ',
    8,
    '{"priority": "highest", "sprint": 0}'
);

COMMENT ON TABLE evolution.intent_graph IS 'The consciousness substrate of the Aether Protocol - tracks all system intentions';
COMMENT ON COLUMN evolution.intent_graph.polarity IS 'Spectrum from -1 (destructive) to +1 (constructive) replacing binary garbage flag';
COMMENT ON COLUMN evolution.intent_graph.vibration_frequency IS 'Energy level 1-10, higher means more active/urgent';
COMMENT ON COLUMN evolution.intent_graph.coherence_score IS 'How aligned this intent is with its parent and children';
COMMENT ON COLUMN evolution.intent_graph.entanglement_keys IS 'Quantum entanglement - intents that affect each other non-locally';