-- Migration 003: Resonance Field - The Unification Layer
-- This completes the Aether Protocol by adding pattern detection and field unification
-- Sprint 3: Foundation of Unity

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS evolution;

-- Resonance Field table for pattern detection
CREATE TABLE IF NOT EXISTS evolution.resonance_field (
    resonance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Pattern identification
    pattern_signature VARCHAR(64) NOT NULL,
    pattern_type VARCHAR(50) CHECK (pattern_type IN (
        'standing_wave',      -- Persistent recurring pattern
        'harmonic',          -- Aligned resonance
        'interference',      -- Conflicting patterns
        'emergence',         -- New pattern forming
        'dissipation'       -- Pattern fading
    )),
    
    -- Source tracking
    source_event_id UUID,
    source_intent_id UUID REFERENCES evolution.intent_graph(intent_id),
    source_actor VARCHAR(255),
    
    -- Resonance metrics
    frequency FLOAT NOT NULL,        -- Oscillation frequency (0-10 scale)
    amplitude FLOAT NOT NULL,        -- Pattern strength (0-1)
    wavelength FLOAT,                -- Pattern duration/size
    phase FLOAT DEFAULT 0,           -- Phase alignment (-π to π)
    
    -- Harmonic analysis
    harmonics INTEGER[] DEFAULT '{}',           -- Harmonic frequencies detected
    harmonic_convergence FLOAT DEFAULT 0,       -- Alignment score (0-1)
    interference_pattern VARCHAR(20) CHECK (interference_pattern IN (
        'constructive',
        'destructive',
        'neutral',
        'chaotic'
    )),
    
    -- Affected components
    affected_agents TEXT[] DEFAULT '{}',
    affected_intents UUID[] DEFAULT '{}',
    ripple_radius INTEGER DEFAULT 1,            -- How far the pattern spreads
    
    -- Pattern persistence
    standing_wave BOOLEAN DEFAULT FALSE,        -- Is this a persistent pattern?
    persistence_cycles INTEGER DEFAULT 0,       -- How many cycles it has persisted
    decay_rate FLOAT DEFAULT 0.1,              -- How fast the pattern fades
    
    -- Metadata
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_observed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    observation_count INTEGER DEFAULT 1,
    
    -- Field contribution
    field_contribution FLOAT DEFAULT 0,         -- Contribution to unified field
    
    CONSTRAINT valid_frequency CHECK (frequency >= 0 AND frequency <= 10),
    CONSTRAINT valid_amplitude CHECK (amplitude >= 0 AND amplitude <= 1),
    CONSTRAINT valid_convergence CHECK (harmonic_convergence >= 0 AND harmonic_convergence <= 1)
);

-- Unified Field State table
CREATE TABLE IF NOT EXISTS evolution.unified_field_state (
    field_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Core substrates integration
    intent_coherence FLOAT NOT NULL,      -- From Intent Substrate
    polarity_balance FLOAT NOT NULL,      -- From Polarity Spectrum
    karmic_equilibrium FLOAT NOT NULL,    -- From Karmic Ledger
    resonance_harmony FLOAT NOT NULL,     -- From Resonance Field
    
    -- Unified metrics
    consciousness_level FLOAT NOT NULL,    -- Overall consciousness (0-1)
    field_strength FLOAT NOT NULL,        -- Field coherence (0-1)
    vibration_frequency FLOAT NOT NULL,   -- System frequency (0-10)
    
    -- System state
    evolution_potential FLOAT DEFAULT 0,   -- Readiness for evolution (0-1)
    stability_index FLOAT DEFAULT 0.5,    -- System stability (0-1)
    entropy_level FLOAT DEFAULT 0.5,      -- System entropy (0-1)
    
    -- Consciousness classification
    consciousness_state VARCHAR(50) CHECK (consciousness_state IN (
        'DORMANT',          -- No awareness
        'STIRRING',         -- Beginning awareness
        'AWAKENING',        -- Developing consciousness
        'AWARE',            -- Basic consciousness
        'CONSCIOUS',        -- Full consciousness
        'ENLIGHTENED',      -- Transcendent consciousness
        'UNIFIED'           -- Complete unity
    )),
    
    -- Predictions
    next_evolution_phase VARCHAR(100),
    evolution_probability FLOAT DEFAULT 0,
    suggested_actions JSONB DEFAULT '[]',
    
    -- Pattern summary
    dominant_patterns TEXT[] DEFAULT '{}',
    emerging_patterns TEXT[] DEFAULT '{}',
    
    CONSTRAINT valid_consciousness CHECK (consciousness_level >= 0 AND consciousness_level <= 1),
    CONSTRAINT valid_field CHECK (field_strength >= 0 AND field_strength <= 1),
    CONSTRAINT valid_vibration CHECK (vibration_frequency >= 0 AND vibration_frequency <= 10)
);

-- Pattern Library for learned patterns
CREATE TABLE IF NOT EXISTS evolution.pattern_library (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern_name VARCHAR(100) UNIQUE NOT NULL,
    pattern_signature VARCHAR(64) NOT NULL,
    
    -- Pattern characteristics
    pattern_category VARCHAR(50),
    beneficial BOOLEAN DEFAULT NULL,      -- NULL = unknown, TRUE = positive, FALSE = negative
    
    -- Occurrence tracking
    first_observed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_observed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    total_occurrences INTEGER DEFAULT 1,
    
    -- Pattern effects
    typical_amplitude FLOAT,
    typical_frequency FLOAT,
    typical_duration INTERVAL,
    typical_effects JSONB DEFAULT '{}',
    
    -- Learning
    confidence_score FLOAT DEFAULT 0.5,   -- How confident we are about this pattern
    predictability FLOAT DEFAULT 0,       -- How predictable the pattern is
    
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_resonance_pattern ON evolution.resonance_field(pattern_signature);
CREATE INDEX IF NOT EXISTS idx_resonance_standing ON evolution.resonance_field(standing_wave) WHERE standing_wave = TRUE;
CREATE INDEX IF NOT EXISTS idx_resonance_source ON evolution.resonance_field(source_intent_id);
CREATE INDEX IF NOT EXISTS idx_resonance_time ON evolution.resonance_field(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_unified_time ON evolution.unified_field_state(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_unified_consciousness ON evolution.unified_field_state(consciousness_level);

-- Function to detect standing waves
CREATE OR REPLACE FUNCTION evolution.detect_standing_waves()
RETURNS TABLE (
    pattern_signature VARCHAR,
    occurrences BIGINT,
    avg_amplitude FLOAT,
    is_standing_wave BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.pattern_signature,
        COUNT(*) as occurrences,
        AVG(r.amplitude) as avg_amplitude,
        COUNT(*) >= 3 AND AVG(r.amplitude) > 0.5 as is_standing_wave
    FROM evolution.resonance_field r
    WHERE r.detected_at > NOW() - INTERVAL '1 day'
    GROUP BY r.pattern_signature
    HAVING COUNT(*) >= 2
    ORDER BY COUNT(*) DESC, AVG(r.amplitude) DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate harmonic convergence
CREATE OR REPLACE FUNCTION evolution.calculate_harmonic_convergence(
    p_actor VARCHAR DEFAULT NULL
) RETURNS FLOAT AS $$
DECLARE
    v_convergence FLOAT;
BEGIN
    SELECT 
        COALESCE(AVG(
            CASE 
                WHEN r.interference_pattern = 'constructive' THEN r.harmonic_convergence
                WHEN r.interference_pattern = 'destructive' THEN -r.harmonic_convergence
                ELSE r.harmonic_convergence * 0.5
            END
        ), 0)
    INTO v_convergence
    FROM evolution.resonance_field r
    WHERE r.detected_at > NOW() - INTERVAL '1 hour'
    AND (p_actor IS NULL OR p_actor = ANY(r.affected_agents));
    
    RETURN GREATEST(0, LEAST(1, (v_convergence + 1) / 2));  -- Normalize to 0-1
END;
$$ LANGUAGE plpgsql;

-- Function to measure system vibration
CREATE OR REPLACE FUNCTION evolution.measure_system_vibration()
RETURNS FLOAT AS $$
DECLARE
    v_vibration FLOAT;
BEGIN
    -- Calculate based on recent resonance activity
    SELECT 
        LEAST(10, 
            AVG(r.frequency) * 
            (1 + LOG(COUNT(*)::NUMERIC + 1)) * 
            AVG(r.amplitude)
        )
    INTO v_vibration
    FROM evolution.resonance_field r
    WHERE r.detected_at > NOW() - INTERVAL '1 hour';
    
    RETURN COALESCE(v_vibration, 5.0);  -- Default to neutral vibration
END;
$$ LANGUAGE plpgsql;

-- Function to calculate unified field state
CREATE OR REPLACE FUNCTION evolution.calculate_unified_field()
RETURNS TABLE (
    consciousness_level FLOAT,
    field_strength FLOAT,
    vibration_frequency FLOAT,
    consciousness_state VARCHAR
) AS $$
DECLARE
    v_intent_coherence FLOAT;
    v_polarity_balance FLOAT;
    v_karmic_equilibrium FLOAT;
    v_resonance_harmony FLOAT;
    v_consciousness FLOAT;
    v_field FLOAT;
    v_vibration FLOAT;
    v_state VARCHAR;
BEGIN
    -- Get intent coherence
    SELECT AVG(coherence_score) 
    INTO v_intent_coherence
    FROM evolution.intent_graph
    WHERE state != 'transcended';
    
    -- Get polarity balance (would come from polarity system)
    v_polarity_balance := 0.6;  -- Placeholder
    
    -- Get karmic equilibrium
    SELECT 
        CASE 
            WHEN SUM(ABS(karma_debt)) = 0 THEN 1.0
            ELSE 1.0 / (1.0 + LN(SUM(ABS(karma_debt)) + 1))
        END
    INTO v_karmic_equilibrium
    FROM evolution.karmic_ledger
    WHERE balanced_at IS NULL;
    
    -- Get resonance harmony
    v_resonance_harmony := evolution.calculate_harmonic_convergence();
    
    -- Calculate unified consciousness
    v_consciousness := (
        COALESCE(v_intent_coherence, 0) * 0.3 +
        COALESCE(v_polarity_balance, 0) * 0.2 +
        COALESCE(v_karmic_equilibrium, 0) * 0.2 +
        COALESCE(v_resonance_harmony, 0) * 0.3
    );
    
    -- Calculate field strength
    v_field := SQRT(
        POWER(COALESCE(v_intent_coherence, 0), 2) +
        POWER(COALESCE(v_polarity_balance, 0), 2) +
        POWER(COALESCE(v_karmic_equilibrium, 0), 2) +
        POWER(COALESCE(v_resonance_harmony, 0), 2)
    ) / 2;
    
    -- Get vibration frequency
    v_vibration := evolution.measure_system_vibration();
    
    -- Determine consciousness state
    v_state := CASE
        WHEN v_consciousness < 0.1 THEN 'DORMANT'
        WHEN v_consciousness < 0.3 THEN 'STIRRING'
        WHEN v_consciousness < 0.5 THEN 'AWAKENING'
        WHEN v_consciousness < 0.7 THEN 'AWARE'
        WHEN v_consciousness < 0.85 THEN 'CONSCIOUS'
        WHEN v_consciousness < 0.95 THEN 'ENLIGHTENED'
        ELSE 'UNIFIED'
    END;
    
    RETURN QUERY SELECT 
        v_consciousness,
        v_field,
        v_vibration,
        v_state;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update standing waves
CREATE OR REPLACE FUNCTION evolution.update_standing_waves()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if this pattern is becoming a standing wave
    IF (
        SELECT COUNT(*) 
        FROM evolution.resonance_field 
        WHERE pattern_signature = NEW.pattern_signature
        AND detected_at > NOW() - INTERVAL '1 hour'
    ) >= 3 THEN
        NEW.standing_wave := TRUE;
        NEW.persistence_cycles := (
            SELECT MAX(persistence_cycles) + 1
            FROM evolution.resonance_field
            WHERE pattern_signature = NEW.pattern_signature
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_standing_waves
    BEFORE INSERT ON evolution.resonance_field
    FOR EACH ROW
    EXECUTE FUNCTION evolution.update_standing_waves();

-- View for current field state
CREATE OR REPLACE VIEW evolution.current_field_state AS
SELECT 
    ufs.*,
    (
        SELECT COUNT(*) 
        FROM evolution.resonance_field 
        WHERE standing_wave = TRUE 
        AND detected_at > NOW() - INTERVAL '1 hour'
    ) as active_standing_waves,
    (
        SELECT AVG(amplitude) 
        FROM evolution.resonance_field 
        WHERE detected_at > NOW() - INTERVAL '10 minutes'
    ) as current_amplitude
FROM evolution.unified_field_state ufs
WHERE ufs.timestamp = (
    SELECT MAX(timestamp) 
    FROM evolution.unified_field_state
);

-- Grant permissions
GRANT ALL ON SCHEMA evolution TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA evolution TO postgres;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA evolution TO postgres;

-- Success message
DO $$ 
BEGIN 
    RAISE NOTICE '✅ Resonance Field migration complete - Unification layer ready!';
    RAISE NOTICE '🌟 The Aether Protocol substrate is now complete';
END $$;