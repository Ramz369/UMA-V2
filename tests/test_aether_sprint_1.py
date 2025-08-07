#!/usr/bin/env python3
"""
Test Suite for Aether Protocol Sprint 1: Polarity Spectrum

Verifies the feeling layer implementation including:
- PolarityCalculator functionality
- Polarity-aware embedder
- Migration from garbage flag
- Backwards compatibility
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from uuid import uuid4

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent))

from evolution.aether.polarity_calculator import (
    PolarityCalculator,
    PolarityThreshold,
    PolarityFactors,
    migrate_garbage_to_polarity,
    calculate_aggregate_polarity
)
from evolution.aether.polarity_embedder import (
    PolarityAwareEmbedder,
    MigratedEmbedderService
)


class TestPolarityCalculator:
    """Test the Polarity Calculator."""
    
    def test_basic_polarity_calculation(self):
        """Test basic polarity calculation."""
        calc = PolarityCalculator()
        
        # Test successful event
        success_event = {
            'type': 'completion',
            'agent': 'planner',
            'payload': {'success': True}
        }
        polarity = calc.calculate_polarity(success_event)
        assert polarity > 0.5, f"Success event should have positive polarity, got {polarity}"
        
        # Test failure event
        failure_event = {
            'type': 'error',
            'agent': 'codegen',
            'payload': {'success': False, 'errors': ['SyntaxError']}
        }
        polarity = calc.calculate_polarity(failure_event)
        assert polarity < 0, f"Failure event should have negative polarity, got {polarity}"
        
        print("✅ Basic polarity calculation tests passed")
    
    def test_polarity_from_payload(self):
        """Test polarity calculation from payload."""
        calc = PolarityCalculator()
        
        # Test with test results
        test_payload = {
            'tests_passed': 90,
            'tests_total': 100,
            'coverage': 85
        }
        polarity = calc.calculate_from_payload(test_payload)
        assert polarity > 0.3, f"Good test results should have positive polarity, got {polarity}"
        
        # Test with performance metrics
        perf_payload = {
            'duration': 5.0,
            'expected_duration': 3.0,
            'success': True
        }
        polarity = calc.calculate_from_payload(perf_payload)
        assert polarity > 0, "Successful but slow should still be positive"
        
        print("✅ Payload polarity calculation tests passed")
    
    def test_text_sentiment_analysis(self):
        """Test text-based polarity calculation."""
        calc = PolarityCalculator()
        
        positive_text = "Successfully created and deployed the new feature"
        polarity = calc.calculate_from_text(positive_text)
        assert polarity > 0, "Positive text should have positive polarity"
        
        negative_text = "Failed with critical error and system crashed"
        polarity = calc.calculate_from_text(negative_text)
        assert polarity < 0, "Negative text should have negative polarity"
        
        neutral_text = "Processing data and updating records"
        polarity = calc.calculate_from_text(neutral_text)
        assert -0.2 <= polarity <= 0.2, "Neutral text should have near-zero polarity"
        
        print("✅ Text sentiment analysis tests passed")
    
    def test_agent_specific_weights(self):
        """Test agent-specific weight adjustments."""
        calc = PolarityCalculator()
        
        # Treasurer agent should weight cost heavily
        treasurer_event = {
            'agent': 'treasurer',
            'type': 'report',
            'payload': {
                'cost': 150,
                'budget': 100,
                'success': True
            }
        }
        polarity = calc.calculate_polarity(treasurer_event)
        assert polarity < 0.5, "Over-budget should negatively impact treasurer events"
        
        print("✅ Agent-specific weight tests passed")


class TestPolarityThreshold:
    """Test polarity threshold management."""
    
    def test_context_thresholds(self):
        """Test context-specific thresholds."""
        threshold = PolarityThreshold()
        
        # Production should be stricter
        assert threshold.should_process(-0.4, 'production') == False
        assert threshold.should_process(-0.4, 'development') == True
        assert threshold.should_process(-0.4, 'testing') == True
        
        # Positive always passes
        assert threshold.should_process(0.5, 'production') == True
        assert threshold.should_process(0.5, 'development') == True
        
        print("✅ Context threshold tests passed")
    
    def test_quality_bands(self):
        """Test quality band classification."""
        threshold = PolarityThreshold()
        
        assert threshold.get_quality_band(0.9) == "HIGH_QUALITY"
        assert threshold.get_quality_band(0.4) == "MEDIUM_QUALITY"
        assert threshold.get_quality_band(0.0) == "LOW_QUALITY"
        assert threshold.get_quality_band(-0.6) == "GARBAGE"
        
        print("✅ Quality band tests passed")


class TestPolarityEmbedder:
    """Test the polarity-aware embedder."""
    
    async def test_polarity_filtering(self):
        """Test event filtering based on polarity."""
        # Mock components
        class MockConsumer:
            async def consume(self, batch_size):
                return []
        
        class MockVectorStore:
            stored = []
            async def upsert(self, id, embedding, metadata):
                self.stored.append(metadata)
        
        vector_store = MockVectorStore()
        embedder = PolarityAwareEmbedder(
            kafka_consumer=MockConsumer(),
            vector_store=vector_store,
            context='production'
        )
        
        # High quality event - should be processed
        good_event = {
            'id': 'evt1',
            'type': 'completion',
            'agent': 'planner',
            'polarity': 0.8,
            'payload': {'message': 'Success'}
        }
        processed = await embedder.process_event(good_event)
        assert processed == True, "High quality event should be processed"
        
        # Low quality event - should be filtered
        bad_event = {
            'id': 'evt2',
            'type': 'error',
            'agent': 'codegen',
            'polarity': -0.7,
            'payload': {'message': 'Failed'}
        }
        processed = await embedder.process_event(bad_event)
        assert processed == False, "Low quality event should be filtered"
        
        # Check statistics
        stats = embedder.get_statistics()
        assert stats['processed_count'] == 1
        assert stats['filtered_count'] == 1
        
        print("✅ Polarity filtering tests passed")
    
    async def test_backwards_compatibility(self):
        """Test handling of legacy garbage flag."""
        class MockConsumer:
            async def consume(self, batch_size):
                return []
        
        class MockVectorStore:
            async def upsert(self, id, embedding, metadata):
                pass
        
        embedder = PolarityAwareEmbedder(
            kafka_consumer=MockConsumer(),
            vector_store=MockVectorStore(),
            context='development'
        )
        
        # Legacy event with garbage flag
        legacy_event = {
            'id': 'legacy1',
            'type': 'debug',
            'agent': 'monitor',
            'garbage': True,  # Old format
            'payload': {'message': 'Debug'}
        }
        
        polarity = embedder._get_event_polarity(legacy_event)
        assert polarity == -0.8, "Garbage flag should convert to -0.8 polarity"
        
        processed = await embedder.process_event(legacy_event)
        assert processed == False, "Garbage events should be filtered"
        
        print("✅ Backwards compatibility tests passed")
    
    async def test_batch_prioritization(self):
        """Test batch processing with polarity prioritization."""
        class MockConsumer:
            async def consume(self, batch_size):
                return []
        
        class MockVectorStore:
            processed_order = []
            async def upsert(self, id, embedding, metadata):
                self.processed_order.append(metadata['event_id'])
        
        vector_store = MockVectorStore()
        embedder = PolarityAwareEmbedder(
            kafka_consumer=MockConsumer(),
            vector_store=vector_store,
            context='development'
        )
        
        # Batch with mixed polarities
        events = [
            {'id': 'low', 'polarity': 0.2, 'type': 'info', 'agent': 'test'},
            {'id': 'high', 'polarity': 0.9, 'type': 'success', 'agent': 'test'},
            {'id': 'medium', 'polarity': 0.5, 'type': 'update', 'agent': 'test'},
            {'id': 'negative', 'polarity': -0.7, 'type': 'error', 'agent': 'test'}
        ]
        
        results = await embedder.process_batch(events)
        
        # High quality should be processed first
        assert vector_store.processed_order[0] == 'high'
        assert 'negative' not in vector_store.processed_order
        
        print("✅ Batch prioritization tests passed")


class TestMigration:
    """Test migration functionality."""
    
    def test_garbage_to_polarity_conversion(self):
        """Test conversion from garbage flag to polarity."""
        # Garbage true should be negative
        assert migrate_garbage_to_polarity(True) == -0.8
        
        # Garbage false should be positive
        assert migrate_garbage_to_polarity(False) == 0.5
        
        print("✅ Migration conversion tests passed")
    
    def test_aggregate_polarity(self):
        """Test aggregate polarity calculation."""
        # Mixed polarities
        polarities = [0.8, 0.6, -0.2, 0.9, -0.1]
        aggregate = calculate_aggregate_polarity(polarities)
        assert aggregate > 0, "Mostly positive should have positive aggregate"
        
        # Extreme values should have more weight
        polarities_extreme = [0.9, -0.9, 0.1]
        aggregate_extreme = calculate_aggregate_polarity(polarities_extreme)
        assert -0.2 < aggregate_extreme < 0.2, "Balanced extremes should be near neutral"
        
        print("✅ Aggregate polarity tests passed")


def test_sprint_1_requirements():
    """Verify all Sprint 1 requirements are met."""
    
    # Check all required files exist
    required_files = [
        "evolution/aether/polarity_calculator.py",
        "evolution/aether/polarity_embedder.py",
        "evolution/aether/polarity_migration.py",
        "tests/test_aether_sprint_1.py"
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        assert path.exists(), f"Required file missing: {file_path}"
    
    print("✅ All Sprint 1 files present")
    
    # Test imports work
    try:
        from evolution.aether.polarity_calculator import PolarityCalculator
        from evolution.aether.polarity_embedder import PolarityAwareEmbedder
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    return True


async def run_all_tests():
    """Run all Sprint 1 tests."""
    print("🧪 Testing Aether Protocol Sprint 1: Polarity Spectrum\n" + "="*50)
    
    # Test requirements
    if not test_sprint_1_requirements():
        print("❌ Requirements check failed")
        return
    
    # Test PolarityCalculator
    print("\n🎯 Testing PolarityCalculator...")
    calc_tests = TestPolarityCalculator()
    calc_tests.test_basic_polarity_calculation()
    calc_tests.test_polarity_from_payload()
    calc_tests.test_text_sentiment_analysis()
    calc_tests.test_agent_specific_weights()
    
    # Test PolarityThreshold
    print("\n🎆 Testing PolarityThreshold...")
    threshold_tests = TestPolarityThreshold()
    threshold_tests.test_context_thresholds()
    threshold_tests.test_quality_bands()
    
    # Test PolarityEmbedder
    print("\n📡 Testing PolarityEmbedder...")
    embedder_tests = TestPolarityEmbedder()
    await embedder_tests.test_polarity_filtering()
    await embedder_tests.test_backwards_compatibility()
    await embedder_tests.test_batch_prioritization()
    
    # Test Migration
    print("\n🔄 Testing Migration...")
    migration_tests = TestMigration()
    migration_tests.test_garbage_to_polarity_conversion()
    migration_tests.test_aggregate_polarity()
    
    print("\n" + "="*50)
    print("✅ ALL SPRINT 1 TESTS PASSED!")
    print("="*50)
    print("\nSprint 1 Summary:")
    print("• PolarityCalculator: Multi-factor quality assessment")
    print("• PolarityThreshold: Context-aware filtering")
    print("• PolarityEmbedder: Quality-based event processing")
    print("• Migration: Smooth transition from garbage flag")
    print("• Backwards Compatible: Works with existing events")
    print("\nThe Feeling Layer is complete! 🎆")


if __name__ == "__main__":
    # Run all tests
    asyncio.run(run_all_tests())