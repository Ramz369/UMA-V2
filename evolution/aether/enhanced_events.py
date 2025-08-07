#!/usr/bin/env python3
"""
Enhanced Event System with Aether Protocol Integration

Extends the base EventMeta and EventEnvelope to include consciousness tracking
through the Intent Substrate. This creates a backwards-compatible enhancement
that can be gradually adopted across the system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

# Import base classes
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from semloop_models.event_envelope import EventMeta as BaseEventMeta, EventEnvelope as BaseEventEnvelope


class AetherEventMeta(BaseEventMeta):
    """
    Enhanced EventMeta with Aether Protocol fields.
    
    Extends the base EventMeta to include consciousness tracking through
    the Intent Substrate. All fields are optional for backwards compatibility.
    """
    
    # Intent Substrate (Consciousness)
    intent_id: Optional[UUID] = Field(
        None,
        description="ID of the intent this event serves (consciousness tracking)"
    )
    intent_depth: int = Field(
        0,
        ge=0,
        description="Depth in the intent hierarchy (0=root, higher=deeper)"
    )
    intent_coherence: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Alignment with parent intent (1.0=perfect coherence)"
    )
    
    # Resonance Substrate (Energy) - Prepared for Sprint 3
    resonance_pattern: Optional[str] = Field(
        None,
        description="Pattern signature for resonance detection"
    )
    vibration_level: int = Field(
        5,
        ge=1,
        le=10,
        description="Energy vibration level (1=low, 10=high)"
    )
    
    # Karma Substrate (Balance) - Prepared for Sprint 2
    karma_impact: float = Field(
        0.0,
        description="Karmic impact of this event (+positive, -negative)"
    )
    karma_actor: Optional[str] = Field(
        None,
        description="Actor responsible for karmic impact"
    )


class AetherEventEnvelope(BaseEventEnvelope):
    """
    Enhanced EventEnvelope with Aether Protocol support.
    
    Key enhancement: Replaces binary 'garbage' flag with polarity spectrum.
    This will be fully implemented in Sprint 1.
    """
    
    meta: AetherEventMeta = Field(
        ...,
        description="Enhanced event metadata with Aether fields"
    )
    
    # Polarity Spectrum (replacing garbage flag) - Sprint 1
    polarity: float = Field(
        0.0,
        ge=-1.0,
        le=1.0,
        description="Event outcome: -1.0 (failure) to +1.0 (perfect success)"
    )
    
    def is_high_quality(self) -> bool:
        """
        Check if event should be processed.
        
        Overrides base method to use polarity instead of garbage flag.
        During transition, supports both approaches.
        """
        # During transition, check both
        if hasattr(self, 'garbage') and self.garbage:
            return False
        return self.polarity > -0.5  # Configurable threshold
    
    def calculate_unified_score(self) -> float:
        """
        Calculate unified field score for this event.
        
        Combines consciousness (intent), energy (vibration), and balance (karma)
        into a single metric representing the event's contribution to system health.
        """
        # Consciousness component
        consciousness = self.meta.intent_coherence if self.meta.intent_id else 1.0
        
        # Energy component
        energy = self.meta.vibration_level / 10.0
        
        # Balance component (karma normalized to 0-1)
        balance = (1.0 + min(max(self.meta.karma_impact, -1), 1)) / 2.0
        
        # Polarity modifier
        polarity_modifier = (1.0 + self.polarity) / 2.0
        
        # Weighted average
        unified = (
            consciousness * 0.3 +
            energy * 0.2 +
            balance * 0.2 +
            polarity_modifier * 0.3
        )
        
        return unified
    
    def to_base_envelope(self) -> BaseEventEnvelope:
        """
        Convert to base EventEnvelope for backwards compatibility.
        """
        base_meta = BaseEventMeta(
            session_id=self.meta.session_id,
            credits_used=self.meta.credits_used,
            context_hash=self.meta.context_hash,
            parent_event_id=self.meta.parent_event_id,
            correlation_id=self.meta.correlation_id,
            tags=self.meta.tags
        )
        
        base_envelope = BaseEventEnvelope(
            id=self.id,
            type=self.type,
            timestamp=self.timestamp,
            agent=self.agent,
            payload=self.payload,
            meta=base_meta,
            garbage=self.polarity < -0.5,  # Convert polarity to garbage flag
            schema_version="1.1"
        )
        
        return base_envelope
    
    @classmethod
    def from_base_envelope(cls, base: BaseEventEnvelope, intent_id: Optional[UUID] = None):
        """
        Create enhanced envelope from base envelope.
        """
        # Create enhanced meta
        aether_meta = AetherEventMeta(
            session_id=base.meta.session_id,
            credits_used=base.meta.credits_used,
            context_hash=base.meta.context_hash,
            parent_event_id=base.meta.parent_event_id,
            correlation_id=base.meta.correlation_id,
            tags=base.meta.tags,
            intent_id=intent_id
        )
        
        # Convert garbage flag to polarity
        polarity = -1.0 if base.garbage else 0.5
        
        return cls(
            id=base.id,
            type=base.type,
            timestamp=base.timestamp,
            agent=base.agent,
            payload=base.payload,
            meta=aether_meta,
            polarity=polarity,
            schema_version="2.0"  # New schema version for Aether
        )


class IntentAwareEventPublisher:
    """
    Event publisher that automatically injects intent context.
    """
    
    def __init__(self, intent_substrate, base_publisher):
        self.intent_substrate = intent_substrate
        self.base_publisher = base_publisher
        self.current_intent_id: Optional[UUID] = None
        self.intent_stack: List[UUID] = []
    
    def set_intent(self, intent_id: UUID):
        """Set the current intent context."""
        self.current_intent_id = intent_id
        self.intent_stack.append(intent_id)
    
    def pop_intent(self) -> Optional[UUID]:
        """Pop the current intent and restore previous."""
        if self.intent_stack:
            self.intent_stack.pop()
            self.current_intent_id = self.intent_stack[-1] if self.intent_stack else None
            return self.current_intent_id
        return None
    
    async def publish(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publish event with automatic intent injection.
        """
        # Inject intent if available
        if self.current_intent_id and 'meta' in event:
            event['meta']['intent_id'] = str(self.current_intent_id)
            
            # Get intent details for coherence calculation
            intent = await self.intent_substrate.get_intent(self.current_intent_id)
            if intent:
                event['meta']['intent_coherence'] = intent.coherence_score
                event['meta']['vibration_level'] = intent.vibration_frequency
        
        # Calculate polarity if not set
        if 'polarity' not in event:
            event['polarity'] = self._calculate_event_polarity(event)
        
        # Publish through base publisher
        return await self.base_publisher.publish(event)
    
    def _calculate_event_polarity(self, event: Dict[str, Any]) -> float:
        """
        Calculate event polarity based on type and payload.
        """
        # Success/failure indicators
        if event.get('type') == 'error':
            return -0.8
        elif event.get('type') == 'completion':
            return 0.8
        elif 'success' in event.get('payload', {}):
            return 0.9 if event['payload']['success'] else -0.6
        
        # Default neutral-positive
        return 0.3


# Example usage
if __name__ == "__main__":
    import asyncio
    from uuid import uuid4
    
    # Create sample enhanced event
    intent_id = uuid4()
    
    meta = AetherEventMeta(
        session_id="uma-v2-2025-08-08-001",
        credits_used=10,
        intent_id=intent_id,
        intent_depth=2,
        intent_coherence=0.95,
        vibration_level=7,
        karma_impact=0.5,
        karma_actor="Claude"
    )
    
    event = AetherEventEnvelope(
        id=uuid4(),
        type="tool_call",
        timestamp=datetime.utcnow(),
        agent="planner",
        payload={"task": "Design API", "success": True},
        meta=meta,
        polarity=0.8
    )
    
    print("🌟 Enhanced Event:")
    print(f"  Intent ID: {event.meta.intent_id}")
    print(f"  Coherence: {event.meta.intent_coherence}")
    print(f"  Polarity: {event.polarity}")
    print(f"  Unified Score: {event.calculate_unified_score():.2f}")
    print(f"  High Quality: {event.is_high_quality()}")
    
    # Convert to base for backwards compatibility
    base = event.to_base_envelope()
    print(f"\n🔄 Base Event (backwards compatible):")
    print(f"  Garbage flag: {base.garbage}")
    print(f"  Schema: {base.schema_version}")