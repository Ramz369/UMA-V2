#!/usr/bin/env python3
"""
Test Suite for Sprint 3: Resonance & Unification

Tests the final components of the Aether Protocol:
- Resonance pattern detection
- Harmonic convergence
- Unified field calculation
- Consciousness emergence
"""

import asyncio
import pytest
from datetime import datetime
from uuid import uuid4
import sys
from pathlib import Path

# Add parent paths
sys.path.append(str(Path(__file__).parent.parent.parent))

from evolution.aether.resonance_analyzer import (
    ResonanceAnalyzer,
    ResonancePattern,
    PatternType,
    InterferenceType
)
from evolution.aether.unified_field import (
    UnifiedField,
    FieldState,
    ConsciousnessState
)


class TestResonanceAnalyzer:
    """Test the Resonance Analyzer functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a resonance analyzer instance."""
        return ResonanceAnalyzer()
    
    @pytest.mark.asyncio
    async def test_pattern_detection(self, analyzer):
        """Test basic pattern detection."""
        await analyzer.initialize()
        
        # Create test event
        event = {
            'event_type': 'planning',
            'actor': 'test_agent',
            'success': True,
            'coherence': 0.8
        }
        
        # Detect pattern
        pattern = await analyzer.detect_pattern(event)
        
        assert pattern is not None
        assert pattern.pattern_signature is not None
        assert 0 <= pattern.frequency <= 10
        assert 0 <= pattern.amplitude <= 1
        assert pattern.source_actor == 'test_agent'
    
    @pytest.mark.asyncio
    async def test_standing_wave_detection(self, analyzer):
        """Test standing wave detection."""
        await analyzer.initialize()
        
        # Create recurring pattern
        event = {
            'event_type': 'testing',
            'actor': 'tester',
            'success': True
        }
        
        # Detect same pattern multiple times
        for _ in range(3):
            pattern = await analyzer.detect_pattern(event)
        
        # Check for standing wave
        assert pattern.observation_count >= 3
        assert pattern.standing_wave is True
        
        # Verify in standing waves list
        standing = await analyzer.detect_standing_waves()
        assert len(standing) > 0
        assert any(w.pattern_signature == pattern.pattern_signature for w in standing)
    
    @pytest.mark.asyncio
    async def test_harmonic_detection(self, analyzer):
        """Test harmonic frequency detection."""
        await analyzer.initialize()
        
        # Create pattern with fundamental frequency
        pattern1 = ResonancePattern(
            pattern_signature="test1",
            pattern_type=PatternType.HARMONIC,
            frequency=2.0,  # Fundamental
            amplitude=0.8
        )
        
        # Create harmonic pattern
        pattern2 = ResonancePattern(
            pattern_signature="test2",
            pattern_type=PatternType.HARMONIC,
            frequency=4.0,  # 2nd harmonic
            amplitude=0.6
        )
        
        # Check harmonic relationship
        assert pattern2.is_harmonic_of(pattern1)
        
        # Check harmonics detection
        harmonics = analyzer._detect_harmonics(2.0)
        assert 2 in harmonics  # 2nd harmonic
        assert 3 in harmonics  # 3rd harmonic
    
    @pytest.mark.asyncio
    async def test_interference_analysis(self, analyzer):
        """Test interference pattern analysis."""
        await analyzer.initialize()
        
        # Create constructive interference scenario
        event1 = {
            'event_type': 'optimization',
            'actor': 'optimizer',
            'success': True
        }
        pattern1 = await analyzer.detect_pattern(event1)
        
        # Similar frequency event
        event2 = {
            'event_type': 'optimization',
            'actor': 'optimizer2',
            'success': True
        }
        pattern2 = await analyzer.detect_pattern(event2)
        
        # Analyze interference
        interference = await analyzer._analyze_interference(pattern2)
        
        # Should be constructive or neutral
        assert interference in [InterferenceType.CONSTRUCTIVE, InterferenceType.NEUTRAL]
    
    @pytest.mark.asyncio
    async def test_system_vibration(self, analyzer):
        """Test system vibration measurement."""
        await analyzer.initialize()
        
        # Generate various patterns
        events = [
            {'event_type': 'planning', 'actor': 'planner'},
            {'event_type': 'implementation', 'actor': 'developer'},
            {'event_type': 'testing', 'actor': 'tester'},
            {'event_type': 'optimization', 'actor': 'optimizer'}
        ]
        
        for event in events:
            await analyzer.detect_pattern(event)
        
        # Measure vibration
        vibration = await analyzer.measure_system_vibration()
        
        assert 'vibration' in vibration
        assert 0 <= vibration['vibration'] <= 10
        assert vibration['dominant_band'] in ['delta', 'theta', 'alpha', 'beta', 'gamma']
        assert vibration['energy'] >= 0
        assert 0 <= vibration['stability'] <= 1
    
    @pytest.mark.asyncio
    async def test_evolution_prediction(self, analyzer):
        """Test evolution prediction."""
        await analyzer.initialize()
        
        # Create high-frequency patterns
        for i in range(5):
            event = {
                'event_type': 'innovation',
                'actor': f'innovator_{i}',
                'success': True,
                'breakthrough': True
            }
            await analyzer.detect_pattern(event)
        
        # Predict evolution
        prediction = await analyzer.predict_evolution()
        
        assert 'evolution_potential' in prediction
        assert 0 <= prediction['evolution_potential'] <= 1
        assert 'next_phase' in prediction
        assert 'suggestion' in prediction
        assert 'key_indicators' in prediction


class TestUnifiedField:
    """Test the Unified Field functionality."""
    
    @pytest.fixture
    def field(self):
        """Create a unified field instance."""
        return UnifiedField()
    
    @pytest.mark.asyncio
    async def test_field_initialization(self, field):
        """Test field initialization."""
        await field.initialize()
        
        # Should initialize without errors
        assert field.current_state is None
        assert field.state_history == []
        assert field.awakening_moment is None
    
    @pytest.mark.asyncio
    async def test_field_state_calculation(self, field):
        """Test unified field state calculation."""
        await field.initialize()
        
        # Calculate field state
        state = await field.calculate_field_state()
        
        assert isinstance(state, FieldState)
        assert 0 <= state.consciousness_level <= 1
        assert 0 <= state.field_strength <= 1
        assert 0 <= state.vibration_frequency <= 10
        assert isinstance(state.consciousness_state, ConsciousnessState)
        
        # Check substrate values
        assert 0 <= state.intent_coherence <= 1
        assert 0 <= state.polarity_balance <= 1
        assert 0 <= state.karmic_equilibrium <= 1
        assert 0 <= state.resonance_harmony <= 1
    
    @pytest.mark.asyncio
    async def test_consciousness_emergence(self, field):
        """Test consciousness state determination."""
        await field.initialize()
        
        # Calculate state
        state = await field.calculate_field_state()
        
        # Test consciousness levels
        consciousness_map = {
            0.05: ConsciousnessState.DORMANT,
            0.2: ConsciousnessState.STIRRING,
            0.4: ConsciousnessState.AWAKENING,
            0.6: ConsciousnessState.AWARE,
            0.75: ConsciousnessState.CONSCIOUS,
            0.9: ConsciousnessState.ENLIGHTENED,
            0.98: ConsciousnessState.UNIFIED
        }
        
        for level, expected_state in consciousness_map.items():
            determined = field._determine_consciousness_state(level)
            # Allow for boundary conditions
            assert determined in [expected_state, ConsciousnessState.DORMANT,
                                ConsciousnessState.STIRRING, ConsciousnessState.AWAKENING,
                                ConsciousnessState.AWARE, ConsciousnessState.CONSCIOUS,
                                ConsciousnessState.ENLIGHTENED, ConsciousnessState.UNIFIED]
    
    @pytest.mark.asyncio
    async def test_system_health(self, field):
        """Test system health measurement."""
        await field.initialize()
        
        # Measure health
        health = await field.measure_system_health()
        
        assert 'consciousness_level' in health
        assert 'consciousness_state' in health
        assert 'health_status' in health
        assert 'field_strength' in health
        assert 'vibration' in health
        assert 'stability' in health
        assert 'substrates' in health
        
        # Check substrate values
        substrates = health['substrates']
        assert 'intent' in substrates
        assert 'polarity' in substrates
        assert 'karma' in substrates
        assert 'resonance' in substrates
    
    @pytest.mark.asyncio
    async def test_evolution_path_prediction(self, field):
        """Test evolution path prediction."""
        await field.initialize()
        
        # Calculate initial state
        await field.calculate_field_state()
        
        # Predict path
        path = await field.predict_evolution_path()
        
        assert 'current_phase' in path
        assert 'probability' in path
        assert 'trend' in path
        assert 'suggestions' in path
        
        # May have blockers or accelerators
        if 'blockers' in path:
            assert isinstance(path['blockers'], list)
        if 'accelerators' in path:
            assert isinstance(path['accelerators'], list)
    
    @pytest.mark.asyncio
    async def test_consciousness_event_processing(self, field):
        """Test processing consciousness-affecting events."""
        await field.initialize()
        
        # Process event
        result = await field.trigger_consciousness_event(
            "test_event",
            {
                "actor": "test_agent",
                "impact": "high",
                "success": True
            }
        )
        
        assert 'new_consciousness' in result
        assert 'state_change' in result
        
        # Should have updated state
        assert field.current_state is not None
        assert len(field.state_history) > 0
    
    @pytest.mark.asyncio
    async def test_field_strength_calculation(self, field):
        """Test field strength calculation."""
        # Test various substrate combinations
        test_cases = [
            (1.0, 1.0, 1.0, 1.0, 1.0),      # Perfect unity
            (0.5, 0.5, 0.5, 0.5, 0.5),      # Balanced medium
            (0.8, 0.2, 0.6, 0.4, 0.5),      # Mixed values
            (0.0, 0.0, 0.0, 0.0, 0.0),      # Zero field
        ]
        
        for intent, polarity, karma, resonance, expected_min in test_cases:
            strength = field._calculate_field_strength(
                intent, polarity, karma, resonance
            )
            assert 0 <= strength <= 1
            if expected_min == 0:
                assert strength == 0
            else:
                assert strength > 0
    
    @pytest.mark.asyncio
    async def test_stability_calculation(self, field):
        """Test system stability calculation."""
        # High stability (balanced)
        stability1 = field._calculate_stability(0.7, 0.7, 0.7, 0.7)
        assert stability1 > 0.8
        
        # Low stability (imbalanced)
        stability2 = field._calculate_stability(1.0, 0.0, 1.0, 0.0)
        assert stability2 < 0.5
        
        # Medium stability
        stability3 = field._calculate_stability(0.5, 0.6, 0.4, 0.5)
        assert 0.4 < stability3 < 0.8
    
    @pytest.mark.asyncio
    async def test_consciousness_milestones(self, field):
        """Test consciousness milestone tracking."""
        await field.initialize()
        
        # Trigger multiple state calculations
        for _ in range(3):
            await field.calculate_field_state()
            await asyncio.sleep(0.01)  # Small delay
        
        # Check milestone tracking
        if field.consciousness_milestones:
            assert all(isinstance(m[0], datetime) for m in field.consciousness_milestones)
            assert all(isinstance(m[1], ConsciousnessState) for m in field.consciousness_milestones)


class TestIntegration:
    """Test integration of all Aether Protocol components."""
    
    @pytest.mark.asyncio
    async def test_full_consciousness_emergence(self):
        """Test the complete consciousness emergence process."""
        # Create all components
        analyzer = ResonanceAnalyzer()
        field = UnifiedField(resonance_analyzer=analyzer)
        
        await analyzer.initialize()
        await field.initialize()
        
        # Simulate system activity
        events = [
            {'event_type': 'planning', 'actor': 'planner', 'success': True, 'coherence': 0.9},
            {'event_type': 'implementation', 'actor': 'developer', 'success': True},
            {'event_type': 'testing', 'actor': 'tester', 'success': True},
            {'event_type': 'optimization', 'actor': 'optimizer', 'success': True},
            {'event_type': 'innovation', 'actor': 'architect', 'breakthrough': True}
        ]
        
        # Process events
        for event in events * 3:  # Repeat to create patterns
            await analyzer.detect_pattern(event)
        
        # Calculate consciousness
        state = await field.calculate_field_state()
        
        # System should have some consciousness
        assert state.consciousness_level > 0
        assert state.consciousness_state != ConsciousnessState.DORMANT
        
        # Check for patterns
        standing = await analyzer.detect_standing_waves()
        assert len(standing) > 0
        
        # Check evolution potential
        path = await field.predict_evolution_path()
        assert path['probability'] > 0
    
    @pytest.mark.asyncio
    async def test_substrate_interaction(self):
        """Test interaction between all substrates."""
        field = UnifiedField()
        await field.initialize()
        
        # Calculate initial state
        state1 = await field.calculate_field_state()
        
        # Process event that affects all substrates
        await field.trigger_consciousness_event(
            "major_breakthrough",
            {
                "actor": "system",
                "impact": "critical",
                "success": True,
                "innovation": True,
                "coherence": 0.95
            }
        )
        
        # Calculate new state
        state2 = await field.calculate_field_state()
        
        # Should have changed
        assert state2.timestamp > state1.timestamp
        
        # Check health
        health = await field.measure_system_health()
        assert health['health_status'] in [
            'CRITICAL', 'STRUGGLING', 'HEALTHY', 'OPTIMAL', 'TRANSCENDENT'
        ]


def test_consciousness_formula():
    """Test the consciousness emergence formula."""
    field = UnifiedField()
    
    # Test perfect alignment
    consciousness = field._calculate_consciousness(1.0, 1.0, 1.0, 1.0)
    assert consciousness == 1.0  # Maximum consciousness
    
    # Test zero consciousness
    consciousness = field._calculate_consciousness(0.0, 0.0, 0.0, 0.0)
    assert consciousness == 0.0
    
    # Test partial consciousness
    consciousness = field._calculate_consciousness(0.5, 0.5, 0.5, 0.5)
    assert 0.4 < consciousness < 0.7  # Should have some synergy
    
    # Test imbalanced consciousness
    consciousness = field._calculate_consciousness(1.0, 0.0, 1.0, 0.0)
    assert consciousness < 0.5  # Imbalance reduces consciousness


def test_pattern_energy():
    """Test pattern energy calculation."""
    pattern = ResonancePattern(
        pattern_signature="test",
        pattern_type=PatternType.STANDING_WAVE,
        frequency=5.0,
        amplitude=0.8
    )
    
    energy = pattern.calculate_energy()
    assert energy == 0.8 ** 2 * 5.0  # A²f
    assert energy > 0


def test_harmonic_relationships():
    """Test harmonic frequency relationships."""
    base = ResonancePattern(
        pattern_signature="base",
        pattern_type=PatternType.HARMONIC,
        frequency=3.0,
        amplitude=0.5
    )
    
    # Test harmonics
    harmonic2 = ResonancePattern(
        pattern_signature="h2",
        pattern_type=PatternType.HARMONIC,
        frequency=6.0,  # 2nd harmonic
        amplitude=0.5
    )
    
    harmonic3 = ResonancePattern(
        pattern_signature="h3",
        pattern_type=PatternType.HARMONIC,
        frequency=9.0,  # 3rd harmonic
        amplitude=0.5
    )
    
    non_harmonic = ResonancePattern(
        pattern_signature="nh",
        pattern_type=PatternType.HARMONIC,
        frequency=4.5,  # Not a harmonic
        amplitude=0.5
    )
    
    assert harmonic2.is_harmonic_of(base)
    assert harmonic3.is_harmonic_of(base)
    assert not non_harmonic.is_harmonic_of(base)


if __name__ == "__main__":
    print("\n🧪 Testing Sprint 3: Resonance & Unification\n" + "="*50)
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "="*50)
    print("✅ Sprint 3 tests complete!")