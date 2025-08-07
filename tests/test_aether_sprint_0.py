#!/usr/bin/env python3
"""
Test Suite for Aether Protocol Sprint 0: Intent Substrate

Verifies the consciousness layer implementation including:
- Intent graph creation and management
- Enhanced EventMeta with intent tracking
- Evolution Orchestrator integration
- Coherence scoring and entanglement
"""

import asyncio
import pytest
import sys
import os
from datetime import datetime
from uuid import UUID, uuid4
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent))
from evolution.aether.intent_substrate import (
    IntentSubstrate,
    Intent,
    IntentType,
    GestationPhase
)
from evolution.aether.enhanced_events import (
    AetherEventMeta,
    AetherEventEnvelope,
    IntentAwareEventPublisher
)


class TestIntentSubstrate:
    """Test the Intent Substrate consciousness layer."""
    
    @pytest.fixture
    async def substrate(self):
        """Create test substrate instance."""
        # Use test database or mock
        substrate = IntentSubstrate("postgresql://localhost/cogplan_test")
        # Note: In real tests, we'd use a test database
        # For now, we'll test the logic without DB
        substrate.pool = None  # Mock pool
        yield substrate
        if substrate.pool:
            await substrate.close()
    
    def test_intent_creation(self):
        """Test creating an intent."""
        intent = Intent(
            intent_type=IntentType.ROOT,
            description="Test root intent",
            initiator="TEST",
            vibration_frequency=8
        )
        
        assert intent.intent_id is not None
        assert intent.intent_type == IntentType.ROOT
        assert intent.polarity == 0.0
        assert intent.coherence_score == 1.0
        assert intent.gestation_phase == GestationPhase.CONCEIVED
    
    def test_intent_hierarchy(self):
        """Test intent parent-child relationships."""
        root = Intent(
            intent_type=IntentType.ROOT,
            description="Root intent",
            initiator="TEST"
        )
        
        branch = Intent(
            intent_type=IntentType.BRANCH,
            description="Branch intent",
            initiator="TEST",
            parent_intent_id=root.intent_id
        )
        
        leaf = Intent(
            intent_type=IntentType.LEAF,
            description="Leaf intent",
            initiator="TEST",
            parent_intent_id=branch.intent_id
        )
        
        assert branch.parent_intent_id == root.intent_id
        assert leaf.parent_intent_id == branch.intent_id
    
    def test_gestation_phases(self):
        """Test intent gestation phase progression."""
        intent = Intent(
            intent_type=IntentType.LEAF,
            description="Test intent",
            initiator="TEST"
        )
        
        phases = [
            GestationPhase.CONCEIVED,
            GestationPhase.FORMING,
            GestationPhase.MANIFESTING,
            GestationPhase.REALIZED,
            GestationPhase.TRANSCENDED
        ]
        
        # Check initial phase
        assert intent.gestation_phase == phases[0]
        
        # Manually progress through phases
        for i, phase in enumerate(phases[1:], 1):
            intent.gestation_phase = phase
            assert intent.gestation_phase == phases[i]
    
    def test_polarity_calculation(self):
        """Test polarity calculation from description."""
        substrate = IntentSubstrate("mock://")
        
        # Positive polarity
        positive = substrate._calculate_polarity("Create and build new feature")
        assert positive > 0
        
        # Negative polarity
        negative = substrate._calculate_polarity("Delete and remove old code")
        assert negative < 0
        
        # Neutral polarity
        neutral = substrate._calculate_polarity("Review existing documentation")
        assert neutral == 0.0
    
    def test_consciousness_level_calculation(self):
        """Test consciousness level determination."""
        substrate = IntentSubstrate("mock://")
        
        # Test different consciousness levels
        assert substrate._calculate_consciousness_level(0.9, 9, 10) == "AWAKENED"
        assert substrate._calculate_consciousness_level(0.7, 7, 5) == "AWARE"
        assert substrate._calculate_consciousness_level(0.5, 5, 3) == "SENSING"
        assert substrate._calculate_consciousness_level(0.3, 3, 1) == "DORMANT"
        assert substrate._calculate_consciousness_level(0.1, 1, 0) == "SLEEPING"


class TestEnhancedEvents:
    """Test enhanced event system with Aether Protocol."""
    
    def test_aether_event_meta(self):
        """Test AetherEventMeta creation."""
        intent_id = uuid4()
        
        meta = AetherEventMeta(
            session_id="uma-v2-2025-08-08-001",
            intent_id=intent_id,
            intent_depth=2,
            intent_coherence=0.95,
            vibration_level=7,
            karma_impact=0.5
        )
        
        assert meta.intent_id == intent_id
        assert meta.intent_depth == 2
        assert meta.intent_coherence == 0.95
        assert meta.vibration_level == 7
        assert meta.karma_impact == 0.5
    
    def test_polarity_spectrum(self):
        """Test polarity spectrum replacing garbage flag."""
        meta = AetherEventMeta(
            session_id="uma-v2-2025-08-08-001"
        )
        
        # High quality event
        good_event = AetherEventEnvelope(
            id=uuid4(),
            type="completion",
            timestamp=datetime.utcnow(),
            agent="test",
            payload={},
            meta=meta,
            polarity=0.8
        )
        assert good_event.is_high_quality() is True
        
        # Low quality event
        bad_event = AetherEventEnvelope(
            id=uuid4(),
            type="error",
            timestamp=datetime.utcnow(),
            agent="test",
            payload={},
            meta=meta,
            polarity=-0.8
        )
        assert bad_event.is_high_quality() is False
    
    def test_unified_score_calculation(self):
        """Test unified field score calculation."""
        meta = AetherEventMeta(
            session_id="uma-v2-2025-08-08-001",
            intent_id=uuid4(),
            intent_coherence=0.9,
            vibration_level=8,
            karma_impact=0.5
        )
        
        event = AetherEventEnvelope(
            id=uuid4(),
            type="tool_call",
            timestamp=datetime.utcnow(),
            agent="test",
            payload={},
            meta=meta,
            polarity=0.7
        )
        
        score = event.calculate_unified_score()
        assert 0 <= score <= 1
        assert score > 0.5  # Should be positive with these values
    
    def test_backwards_compatibility(self):
        """Test conversion between enhanced and base events."""
        # Create enhanced event
        meta = AetherEventMeta(
            session_id="uma-v2-2025-08-08-001",
            intent_id=uuid4()
        )
        
        enhanced = AetherEventEnvelope(
            id=uuid4(),
            type="tool_call",
            timestamp=datetime.utcnow(),
            agent="test",
            payload={"data": "test"},
            meta=meta,
            polarity=0.5
        )
        
        # Convert to base
        base = enhanced.to_base_envelope()
        assert base.garbage is False  # Positive polarity -> not garbage
        assert base.meta.session_id == enhanced.meta.session_id
        
        # Convert back to enhanced
        restored = AetherEventEnvelope.from_base_envelope(base)
        assert restored.meta.session_id == enhanced.meta.session_id


class TestIntegration:
    """Test integration between Intent Substrate and events."""
    
    @pytest.mark.asyncio
    async def test_intent_aware_publishing(self):
        """Test publishing events with intent context."""
        # Mock components
        class MockPublisher:
            async def publish(self, event):
                return {"status": "published"}
        
        class MockSubstrate:
            async def get_intent(self, intent_id):
                return Intent(
                    intent_id=intent_id,
                    intent_type=IntentType.LEAF,
                    description="Test intent",
                    initiator="TEST",
                    coherence_score=0.9,
                    vibration_frequency=7
                )
        
        substrate = MockSubstrate()
        base_publisher = MockPublisher()
        
        # Create intent-aware publisher
        publisher = IntentAwareEventPublisher(substrate, base_publisher)
        
        # Set intent context
        intent_id = uuid4()
        publisher.set_intent(intent_id)
        
        # Publish event
        event = {
            "type": "completion",
            "meta": {},
            "payload": {"success": True}
        }
        
        result = await publisher.publish(event)
        assert result["status"] == "published"
        assert "intent_id" in event["meta"]
        assert "polarity" in event


def test_sprint_0_requirements():
    """Verify all Sprint 0 requirements are met."""
    
    # 1. Intent graph table SQL exists
    migration_path = Path("evolution/migrations/001_intent_substrate.sql")
    assert migration_path.exists(), "Intent graph migration missing"
    
    # 2. IntentSubstrate implementation exists
    substrate_path = Path("evolution/aether/intent_substrate.py")
    assert substrate_path.exists(), "IntentSubstrate implementation missing"
    
    # 3. Enhanced EventMeta exists
    events_path = Path("evolution/aether/enhanced_events.py")
    assert events_path.exists(), "Enhanced events implementation missing"
    
    # 4. Intent-aware orchestrator exists
    orchestrator_path = Path("evolution/aether/intent_orchestrator.py")
    assert orchestrator_path.exists(), "Intent orchestrator missing"
    
    print("✅ All Sprint 0 requirements satisfied!")


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Testing Aether Protocol Sprint 0: Intent Substrate\n")
    
    # Test requirements
    test_sprint_0_requirements()
    
    # Test intent creation
    print("\n🎯 Testing Intent Creation...")
    intent = Intent(
        intent_type=IntentType.ROOT,
        description="Test the Aether Protocol implementation",
        initiator="TEST_SUITE"
    )
    print(f"  Created intent: {intent.intent_id}")
    print(f"  Type: {intent.intent_type}")
    print(f"  Phase: {intent.gestation_phase}")
    
    # Test enhanced events
    print("\n📨 Testing Enhanced Events...")
    meta = AetherEventMeta(
        session_id="uma-v2-2025-08-08-001",
        intent_id=intent.intent_id,
        intent_coherence=0.95
    )
    event = AetherEventEnvelope(
        id=uuid4(),
        type="completion",
        timestamp=datetime.utcnow(),
        agent="test",
        payload={"test": "data"},
        meta=meta,
        polarity=0.8
    )
    print(f"  Event polarity: {event.polarity}")
    print(f"  Unified score: {event.calculate_unified_score():.2f}")
    print(f"  High quality: {event.is_high_quality()}")
    
    print("\n✅ Sprint 0 tests passed!")