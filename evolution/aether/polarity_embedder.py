#!/usr/bin/env python3
"""
Polarity-Aware Embedder Service

Enhanced embedder that uses polarity spectrum instead of binary garbage flag.
Part of Sprint 1: Foundation of Feeling.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, Optional, List
from uuid import UUID
from pathlib import Path

# Add parent paths
sys.path.append(str(Path(__file__).parent.parent.parent))

from semloop_models import EventEnvelope
from evolution.aether.polarity_calculator import (
    PolarityCalculator,
    PolarityThreshold,
    migrate_garbage_to_polarity
)
from evolution.aether.enhanced_events import AetherEventEnvelope

logger = logging.getLogger(__name__)


class PolarityAwareEmbedder:
    """
    Enhanced embedder service that uses polarity spectrum for quality filtering.
    
    Key improvements:
    - Continuous quality spectrum instead of binary garbage flag
    - Context-aware thresholds
    - Quality metrics tracking
    - Polarity-based prioritization
    """
    
    def __init__(self,
                 kafka_consumer: Any,
                 vector_store: Any,
                 metrics_client: Optional[Any] = None,
                 context: str = 'default'):
        """
        Initialize polarity-aware embedder.
        
        Args:
            kafka_consumer: Kafka/Redpanda consumer
            vector_store: Vector database client  
            metrics_client: Optional metrics collector
            context: Operating context (production, development, testing)
        """
        self.consumer = kafka_consumer
        self.vector_store = vector_store
        self.metrics = metrics_client
        self.context = context
        
        # Initialize polarity components
        self.polarity_calc = PolarityCalculator()
        self.threshold = PolarityThreshold()
        
        # Statistics
        self.processed_count = 0
        self.filtered_count = 0
        self.polarity_distribution = {
            'excellent': 0,  # >= 0.8
            'good': 0,       # >= 0.5
            'acceptable': 0, # >= 0.2
            'neutral': 0,    # >= -0.2
            'poor': 0,       # >= -0.5
            'critical': 0,   # >= -0.8
            'failure': 0     # < -0.8
        }
        self.cumulative_polarity = 0.0
    
    async def process_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Process a single event with polarity-based filtering.
        
        Args:
            event_data: Raw event data from Kafka
            
        Returns:
            True if processed, False if filtered out
        """
        try:
            # Parse event envelope
            if isinstance(event_data, str):
                event_data = json.loads(event_data)
            
            # Calculate or extract polarity
            polarity = self._get_event_polarity(event_data)
            
            # Update statistics
            self._update_polarity_stats(polarity)
            
            # Apply polarity threshold
            if not self.threshold.should_process(polarity, self.context):
                self.filtered_count += 1
                quality_band = self.threshold.get_quality_band(polarity)
                logger.info(
                    f"Event filtered out - Polarity: {polarity:+.3f}, "
                    f"Quality: {quality_band}, Context: {self.context}"
                )
                
                # Optionally store metadata about filtered events
                await self._log_filtered_event(event_data, polarity)
                return False
            
            # Process high-quality event
            await self._process_high_quality_event(event_data, polarity)
            self.processed_count += 1
            
            # Log processing
            logger.debug(
                f"Event processed - Polarity: {polarity:+.3f}, "
                f"Agent: {event_data.get('agent', 'unknown')}, "
                f"Type: {event_data.get('type', 'unknown')}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            return False
    
    def _get_event_polarity(self, event_data: Dict[str, Any]) -> float:
        """
        Extract or calculate polarity for an event.
        """
        # Check if polarity already exists (Sprint 1 compatible events)
        if 'polarity' in event_data:
            return event_data['polarity']
        
        # Check for legacy garbage flag (backwards compatibility)
        if 'garbage' in event_data:
            return migrate_garbage_to_polarity(event_data['garbage'])
        
        # Calculate polarity from event content
        return self.polarity_calc.calculate_polarity(event_data)
    
    def _update_polarity_stats(self, polarity: float):
        """
        Update polarity distribution statistics.
        """
        self.cumulative_polarity += polarity
        
        if polarity >= 0.8:
            self.polarity_distribution['excellent'] += 1
        elif polarity >= 0.5:
            self.polarity_distribution['good'] += 1
        elif polarity >= 0.2:
            self.polarity_distribution['acceptable'] += 1
        elif polarity >= -0.2:
            self.polarity_distribution['neutral'] += 1
        elif polarity >= -0.5:
            self.polarity_distribution['poor'] += 1
        elif polarity >= -0.8:
            self.polarity_distribution['critical'] += 1
        else:
            self.polarity_distribution['failure'] += 1
    
    async def _process_high_quality_event(self, event_data: Dict[str, Any], polarity: float):
        """
        Process events that pass the polarity threshold.
        """
        # Generate embedding with polarity weighting
        embedding = await self._generate_embedding(event_data, polarity)
        
        # Store in vector database with polarity metadata
        metadata = {
            'event_id': event_data.get('id'),
            'agent': event_data.get('agent'),
            'type': event_data.get('type'),
            'polarity': polarity,
            'quality_band': self.threshold.get_quality_band(polarity),
            'timestamp': event_data.get('timestamp')
        }
        
        await self.vector_store.upsert(
            id=event_data.get('id'),
            embedding=embedding,
            metadata=metadata
        )
    
    async def _generate_embedding(self, event_data: Dict[str, Any], polarity: float) -> List[float]:
        """
        Generate embedding for event, weighted by polarity.
        """
        # Extract text content
        text_parts = []
        
        # Add type and agent
        text_parts.append(f"type:{event_data.get('type', 'unknown')}")
        text_parts.append(f"agent:{event_data.get('agent', 'unknown')}")
        
        # Add payload content
        payload = event_data.get('payload', {})
        if isinstance(payload, dict):
            for key, value in payload.items():
                if isinstance(value, (str, int, float, bool)):
                    text_parts.append(f"{key}:{value}")
        
        # Add polarity as semantic signal
        text_parts.append(f"quality:{polarity:+.3f}")
        
        text = " ".join(text_parts)
        
        # Generate actual embedding (placeholder - would use real model)
        # In production, this would call sentence-transformers or similar
        embedding = [polarity] * 384  # Placeholder 384-dim vector
        
        # Weight embedding by polarity (higher quality = stronger signal)
        weight = abs(polarity) + 0.5
        embedding = [v * weight for v in embedding]
        
        return embedding
    
    async def _log_filtered_event(self, event_data: Dict[str, Any], polarity: float):
        """
        Log filtered events for analysis.
        """
        # Could write to a separate topic or database for analysis
        if self.metrics:
            await self.metrics.increment(
                'embedder.filtered_events',
                tags={
                    'quality_band': self.threshold.get_quality_band(polarity),
                    'agent': event_data.get('agent', 'unknown'),
                    'type': event_data.get('type', 'unknown')
                }
            )
    
    async def process_batch(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of events with polarity-based prioritization.
        """
        # Calculate polarities for all events
        polarized_events = [
            (event, self._get_event_polarity(event))
            for event in events
        ]
        
        # Sort by polarity (process highest quality first)
        polarized_events.sort(key=lambda x: x[1], reverse=True)
        
        # Process in quality order
        results = {
            'processed': 0,
            'filtered': 0,
            'errors': 0
        }
        
        for event, polarity in polarized_events:
            try:
                if await self.process_event(event):
                    results['processed'] += 1
                else:
                    results['filtered'] += 1
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                results['errors'] += 1
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get embedder statistics with polarity insights.
        """
        total_events = self.processed_count + self.filtered_count
        avg_polarity = (
            self.cumulative_polarity / total_events 
            if total_events > 0 else 0.0
        )
        
        return {
            'processed_count': self.processed_count,
            'filtered_count': self.filtered_count,
            'filter_rate': self.filtered_count / max(total_events, 1),
            'average_polarity': avg_polarity,
            'polarity_distribution': self.polarity_distribution,
            'context': self.context,
            'threshold': self.threshold.context_thresholds.get(
                self.context,
                self.threshold.default_threshold
            )
        }
    
    async def run(self):
        """
        Main processing loop.
        """
        logger.info(
            f"Starting Polarity-Aware Embedder in {self.context} context"
        )
        logger.info(
            f"Polarity threshold: "
            f"{self.threshold.context_thresholds.get(self.context, -0.5)}"
        )
        
        while True:
            try:
                # Consume events from Kafka
                messages = await self.consumer.consume(batch_size=10)
                
                if messages:
                    # Process batch with polarity prioritization
                    results = await self.process_batch(messages)
                    
                    logger.info(
                        f"Batch processed - "
                        f"Processed: {results['processed']}, "
                        f"Filtered: {results['filtered']}, "
                        f"Errors: {results['errors']}"
                    )
                
                # Periodic statistics
                if (self.processed_count + self.filtered_count) % 100 == 0:
                    stats = self.get_statistics()
                    logger.info(f"Embedder Statistics: {json.dumps(stats, indent=2)}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                await asyncio.sleep(5)


# Backwards compatibility wrapper
class MigratedEmbedderService:
    """
    Wrapper to migrate existing EmbedderService to use polarity.
    """
    
    def __init__(self, *args, **kwargs):
        # Extract context if provided
        context = kwargs.pop('context', 'production')
        
        # Create polarity-aware embedder
        self.embedder = PolarityAwareEmbedder(*args, context=context, **kwargs)
        
        # Expose same interface
        self.process_event = self.embedder.process_event
        self.processed_count = property(lambda: self.embedder.processed_count)
        self.skipped_garbage_count = property(lambda: self.embedder.filtered_count)
    
    async def run(self):
        """Run the embedder."""
        await self.embedder.run()


# Example usage and testing
if __name__ == "__main__":
    import json
    
    # Mock components for testing
    class MockConsumer:
        async def consume(self, batch_size):
            return []
    
    class MockVectorStore:
        async def upsert(self, id, embedding, metadata):
            pass
    
    # Test polarity embedder
    embedder = PolarityAwareEmbedder(
        kafka_consumer=MockConsumer(),
        vector_store=MockVectorStore(),
        context='development'
    )
    
    # Test events with different polarities
    test_events = [
        {
            'id': 'evt1',
            'type': 'completion',
            'agent': 'planner',
            'polarity': 0.8,
            'payload': {'message': 'Task completed successfully'}
        },
        {
            'id': 'evt2',
            'type': 'error',
            'agent': 'codegen',
            'polarity': -0.7,
            'payload': {'message': 'Failed to generate code'}
        },
        {
            'id': 'evt3',
            'type': 'info',
            'agent': 'monitor',
            'garbage': True,  # Legacy format
            'payload': {'message': 'Debug output'}
        }
    ]
    
    print("\n🎆 Testing Polarity-Aware Embedder\n" + "="*50)
    
    async def test():
        for event in test_events:
            processed = await embedder.process_event(event)
            polarity = embedder._get_event_polarity(event)
            quality = embedder.threshold.get_quality_band(polarity)
            
            print(f"\nEvent: {event['id']} ({event['type']})")
            print(f"  Polarity: {polarity:+.3f}")
            print(f"  Quality: {quality}")
            print(f"  Processed: {processed}")
        
        # Show statistics
        stats = embedder.get_statistics()
        print("\n" + "="*50)
        print("Statistics:")
        print(f"  Processed: {stats['processed_count']}")
        print(f"  Filtered: {stats['filtered_count']}")
        print(f"  Average Polarity: {stats['average_polarity']:+.3f}")
        print(f"  Distribution: {stats['polarity_distribution']}")
    
    asyncio.run(test())
    print("\n✅ Polarity Embedder ready for Sprint 1!")