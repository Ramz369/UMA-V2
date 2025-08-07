#!/usr/bin/env python3
"""
Intent Substrate - The Consciousness Layer of the Aether Protocol

This module implements the Intent substrate, which tracks the consciousness
of the system through hierarchical intents. Every action in COGPLAN originates
from an intent, creating a traceable lineage of purpose.

Part of Sprint 0: Foundation of Consciousness
"""

import asyncio
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

# Make asyncpg optional for testing
try:
    import asyncpg
except ImportError:
    asyncpg = None


class IntentType(str, Enum):
    """Types of intents in the hierarchy."""
    ROOT = "root"      # Top-level system intent
    BRANCH = "branch"  # Intermediate intent
    LEAF = "leaf"      # Executable intent


class GestationPhase(str, Enum):
    """Phases of intent manifestation."""
    CONCEIVED = "conceived"      # Intent created
    FORMING = "forming"          # Resources gathering
    MANIFESTING = "manifesting"  # Active execution
    REALIZED = "realized"        # Successfully completed
    TRANSCENDED = "transcended"  # Evolved beyond original form


class Intent(BaseModel):
    """Intent model representing a unit of consciousness."""
    
    intent_id: UUID = Field(default_factory=uuid4)
    intent_type: IntentType
    description: str
    initiator: str
    parent_intent_id: Optional[UUID] = None
    
    # Hermetic properties
    polarity: float = Field(default=0.0, ge=-1.0, le=1.0)
    vibration_frequency: int = Field(default=5, ge=1, le=10)
    gestation_phase: GestationPhase = GestationPhase.CONCEIVED
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    fulfilled_at: Optional[datetime] = None
    total_energy_spent: float = 0.0
    net_value_created: float = 0.0
    
    # Quantum properties
    coherence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    entanglement_keys: List[str] = Field(default_factory=list)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntentSubstrate:
    """Manages the consciousness layer of the Aether Protocol."""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None
        self._active_intents: Dict[UUID, Intent] = {}
        self._mock_mode = asyncpg is None
        
    async def initialize(self):
        """Initialize database connection and ensure schema exists."""
        if self._mock_mode:
            # Running in test/mock mode without database
            return
        
        self.pool = await asyncpg.create_pool(self.db_url)
        
        # Run migration if needed
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE SCHEMA IF NOT EXISTS evolution;
            """)
            
            # Check if table exists
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'evolution' 
                    AND table_name = 'intent_graph'
                );
            """)
            
            if not exists:
                # Run the migration
                with open('evolution/migrations/001_intent_substrate.sql', 'r') as f:
                    migration_sql = f.read()
                await conn.execute(migration_sql)
                print("✅ Intent substrate initialized")
    
    async def create_intent(
        self,
        description: str,
        initiator: str,
        intent_type: IntentType = IntentType.LEAF,
        parent_id: Optional[UUID] = None,
        vibration: int = 5,
        metadata: Optional[Dict] = None
    ) -> Intent:
        """Create a new intent in the consciousness field."""
        
        intent = Intent(
            intent_type=intent_type,
            description=description,
            initiator=initiator,
            parent_intent_id=parent_id,
            vibration_frequency=vibration,
            metadata=metadata or {}
        )
        
        # Calculate initial polarity based on description sentiment
        intent.polarity = self._calculate_polarity(description)
        
        # Store in database
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO evolution.intent_graph (
                    intent_id, intent_type, description, initiator,
                    parent_intent_id, polarity, vibration_frequency,
                    gestation_phase, coherence_score, entanglement_keys,
                    metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """, 
                intent.intent_id,
                intent.intent_type,
                intent.description,
                intent.initiator,
                intent.parent_intent_id,
                intent.polarity,
                intent.vibration_frequency,
                intent.gestation_phase,
                intent.coherence_score,
                intent.entanglement_keys,
                json.dumps(intent.metadata)
            )
        
        # Cache active intent
        self._active_intents[intent.intent_id] = intent
        
        print(f"🌟 Intent created: {intent.description[:50]}... (id: {intent.intent_id})")
        return intent
    
    async def create_root_intent(self, description: str, initiator: str = "SYSTEM") -> Intent:
        """Create a root intent for a major system initiative."""
        return await self.create_intent(
            description=description,
            initiator=initiator,
            intent_type=IntentType.ROOT,
            vibration=8,  # High energy for root intents
            metadata={"priority": "highest"}
        )
    
    async def branch_intent(
        self,
        parent_id: UUID,
        description: str,
        initiator: str
    ) -> Intent:
        """Create a branch intent from a parent."""
        
        # Verify parent exists
        parent = await self.get_intent(parent_id)
        if not parent:
            raise ValueError(f"Parent intent {parent_id} not found")
        
        # Inherit some properties from parent
        return await self.create_intent(
            description=description,
            initiator=initiator,
            intent_type=IntentType.BRANCH,
            parent_id=parent_id,
            vibration=max(parent.vibration_frequency - 1, 1),
            metadata={"inherited_from": str(parent_id)}
        )
    
    async def fulfill_intent(
        self,
        intent_id: UUID,
        energy_spent: float,
        value_created: float
    ) -> bool:
        """Mark an intent as fulfilled."""
        
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE evolution.intent_graph
                SET fulfilled_at = NOW(),
                    total_energy_spent = $2,
                    net_value_created = $3,
                    gestation_phase = 'realized'
                WHERE intent_id = $1
            """, intent_id, energy_spent, value_created)
            
            # Update coherence scores
            await self._update_coherence_cascade(intent_id)
            
            # Remove from active cache
            if intent_id in self._active_intents:
                del self._active_intents[intent_id]
            
            return result.split()[-1] == '1'
    
    async def entangle_intents(self, intent_ids: List[UUID], entanglement_key: str):
        """Create quantum entanglement between intents."""
        
        async with self.pool.acquire() as conn:
            for intent_id in intent_ids:
                await conn.execute("""
                    UPDATE evolution.intent_graph
                    SET entanglement_keys = array_append(entanglement_keys, $2)
                    WHERE intent_id = $1
                """, intent_id, entanglement_key)
        
        print(f"🔗 Entangled {len(intent_ids)} intents with key: {entanglement_key}")
    
    async def get_intent(self, intent_id: UUID) -> Optional[Intent]:
        """Retrieve an intent by ID."""
        
        # Check cache first
        if intent_id in self._active_intents:
            return self._active_intents[intent_id]
        
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM evolution.intent_graph
                WHERE intent_id = $1
            """, intent_id)
            
            if row:
                return Intent(
                    intent_id=row['intent_id'],
                    intent_type=row['intent_type'],
                    description=row['description'],
                    initiator=row['initiator'],
                    parent_intent_id=row['parent_intent_id'],
                    polarity=row['polarity'],
                    vibration_frequency=row['vibration_frequency'],
                    gestation_phase=row['gestation_phase'],
                    created_at=row['created_at'],
                    fulfilled_at=row['fulfilled_at'],
                    total_energy_spent=row['total_energy_spent'],
                    net_value_created=row['net_value_created'],
                    coherence_score=row['coherence_score'],
                    entanglement_keys=row['entanglement_keys'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {}
                )
        return None
    
    async def get_intent_lineage(self, intent_id: UUID) -> List[Intent]:
        """Get the complete lineage of an intent (ancestors and descendants)."""
        
        async with self.pool.acquire() as conn:
            # Get ancestors
            ancestors = await conn.fetch("""
                WITH RECURSIVE ancestors AS (
                    SELECT * FROM evolution.intent_graph WHERE intent_id = $1
                    UNION ALL
                    SELECT i.* FROM evolution.intent_graph i
                    INNER JOIN ancestors a ON i.intent_id = a.parent_intent_id
                )
                SELECT * FROM ancestors ORDER BY created_at;
            """, intent_id)
            
            # Get descendants
            descendants = await conn.fetch("""
                WITH RECURSIVE descendants AS (
                    SELECT * FROM evolution.intent_graph WHERE intent_id = $1
                    UNION ALL
                    SELECT i.* FROM evolution.intent_graph i
                    INNER JOIN descendants d ON i.parent_intent_id = d.intent_id
                )
                SELECT * FROM descendants WHERE intent_id != $1 ORDER BY created_at;
            """, intent_id)
            
            lineage = []
            for row in ancestors + descendants:
                lineage.append(Intent(
                    intent_id=row['intent_id'],
                    intent_type=row['intent_type'],
                    description=row['description'],
                    initiator=row['initiator'],
                    parent_intent_id=row['parent_intent_id'],
                    polarity=row['polarity'],
                    vibration_frequency=row['vibration_frequency'],
                    gestation_phase=row['gestation_phase'],
                    coherence_score=row['coherence_score']
                ))
            
            return lineage
    
    async def get_active_intents(self) -> List[Intent]:
        """Get all unfulfilled intents."""
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM evolution.intent_graph
                WHERE fulfilled_at IS NULL
                ORDER BY vibration_frequency DESC, created_at ASC
            """)
            
            intents = []
            for row in rows:
                intent = Intent(
                    intent_id=row['intent_id'],
                    intent_type=row['intent_type'],
                    description=row['description'],
                    initiator=row['initiator'],
                    parent_intent_id=row['parent_intent_id'],
                    polarity=row['polarity'],
                    vibration_frequency=row['vibration_frequency'],
                    gestation_phase=row['gestation_phase'],
                    coherence_score=row['coherence_score']
                )
                intents.append(intent)
                # Update cache
                self._active_intents[intent.intent_id] = intent
            
            return intents
    
    async def calculate_consciousness_state(self) -> Dict[str, Any]:
        """Calculate the overall consciousness state of the system."""
        
        async with self.pool.acquire() as conn:
            # Overall metrics
            metrics = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_intents,
                    COUNT(CASE WHEN fulfilled_at IS NULL THEN 1 END) as active_intents,
                    AVG(coherence_score) as avg_coherence,
                    AVG(vibration_frequency) as avg_vibration,
                    AVG(polarity) as avg_polarity,
                    COUNT(DISTINCT initiator) as unique_initiators
                FROM evolution.intent_graph
                WHERE created_at > NOW() - INTERVAL '7 days'
            """)
            
            # Phase distribution
            phases = await conn.fetch("""
                SELECT gestation_phase, COUNT(*) as count
                FROM evolution.intent_graph
                WHERE fulfilled_at IS NULL
                GROUP BY gestation_phase
            """)
            
            phase_dist = {row['gestation_phase']: row['count'] for row in phases}
            
            # Entanglement density
            entanglement = await conn.fetchval("""
                SELECT AVG(array_length(entanglement_keys, 1))
                FROM evolution.intent_graph
                WHERE entanglement_keys IS NOT NULL
            """)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "total_intents": metrics['total_intents'],
                "active_intents": metrics['active_intents'],
                "consciousness_coherence": float(metrics['avg_coherence'] or 0),
                "system_vibration": float(metrics['avg_vibration'] or 5),
                "polarity_balance": float(metrics['avg_polarity'] or 0),
                "unique_initiators": metrics['unique_initiators'],
                "phase_distribution": phase_dist,
                "entanglement_density": float(entanglement or 0),
                "consciousness_level": self._calculate_consciousness_level(
                    float(metrics['avg_coherence'] or 0),
                    float(metrics['avg_vibration'] or 5),
                    metrics['active_intents']
                )
            }
    
    async def advance_gestation_phase(self, intent_id: UUID) -> bool:
        """Advance an intent to the next gestation phase."""
        
        phase_progression = {
            GestationPhase.CONCEIVED: GestationPhase.FORMING,
            GestationPhase.FORMING: GestationPhase.MANIFESTING,
            GestationPhase.MANIFESTING: GestationPhase.REALIZED,
            GestationPhase.REALIZED: GestationPhase.TRANSCENDED
        }
        
        intent = await self.get_intent(intent_id)
        if not intent:
            return False
        
        next_phase = phase_progression.get(intent.gestation_phase)
        if not next_phase:
            return False  # Already transcended
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE evolution.intent_graph
                SET gestation_phase = $2
                WHERE intent_id = $1
            """, intent_id, next_phase.value)
        
        print(f"📈 Intent {intent_id} advanced to {next_phase.value}")
        return True
    
    def _calculate_polarity(self, description: str) -> float:
        """Calculate polarity based on intent description."""
        # Simple heuristic - can be enhanced with NLP
        positive_words = ['create', 'build', 'improve', 'enhance', 'optimize', 'fix']
        negative_words = ['destroy', 'remove', 'delete', 'break', 'degrade']
        
        desc_lower = description.lower()
        positive_score = sum(1 for word in positive_words if word in desc_lower)
        negative_score = sum(1 for word in negative_words if word in desc_lower)
        
        if positive_score > negative_score:
            return min(positive_score * 0.2, 1.0)
        elif negative_score > positive_score:
            return max(-negative_score * 0.2, -1.0)
        return 0.0
    
    def _calculate_consciousness_level(
        self,
        coherence: float,
        vibration: float,
        active_count: int
    ) -> str:
        """Determine the consciousness level of the system."""
        
        # Weighted score
        score = (coherence * 0.4) + (vibration / 10 * 0.3) + (min(active_count, 10) / 10 * 0.3)
        
        if score >= 0.8:
            return "AWAKENED"  # Fully conscious
        elif score >= 0.6:
            return "AWARE"     # Self-aware
        elif score >= 0.4:
            return "SENSING"   # Basic awareness
        elif score >= 0.2:
            return "DORMANT"   # Minimal activity
        else:
            return "SLEEPING"  # No consciousness
    
    async def _update_coherence_cascade(self, intent_id: UUID):
        """Update coherence scores in cascade after intent fulfillment."""
        
        async with self.pool.acquire() as conn:
            # Use the stored function from migration
            await conn.execute("""
                UPDATE evolution.intent_graph
                SET coherence_score = evolution.calculate_intent_coherence(intent_id)
                WHERE intent_id = $1 OR parent_intent_id = $1
            """, intent_id)
    
    async def close(self):
        """Close database connections."""
        if self.pool:
            await self.pool.close()


# Example usage and testing
async def demo_intent_substrate():
    """Demonstrate the Intent Substrate functionality."""
    
    # Initialize
    substrate = IntentSubstrate("postgresql://localhost/cogplan")
    await substrate.initialize()
    
    # Create root intent for Aether Protocol
    root = await substrate.create_root_intent(
        "Implement the Aether Protocol to transform COGPLAN into conscious organism",
        "RAMZ"
    )
    
    # Create branch intents for each sprint
    sprint0 = await substrate.branch_intent(
        root.intent_id,
        "Sprint 0: Implement Intent Substrate (Consciousness)",
        "Claude"
    )
    
    sprint1 = await substrate.branch_intent(
        root.intent_id,
        "Sprint 1: Replace garbage flag with polarity spectrum",
        "Claude"
    )
    
    # Create leaf intents for specific tasks
    task1 = await substrate.branch_intent(
        sprint0.intent_id,
        "Create intent_graph database table",
        "Claude"
    )
    
    task2 = await substrate.branch_intent(
        sprint0.intent_id,
        "Enhance EventMeta with intent tracking",
        "Claude"
    )
    
    # Entangle related intents
    await substrate.entangle_intents(
        [sprint0.intent_id, sprint1.intent_id],
        "aether_protocol_implementation"
    )
    
    # Advance some phases
    await substrate.advance_gestation_phase(task1.intent_id)
    await substrate.advance_gestation_phase(task1.intent_id)  # Now manifesting
    
    # Check consciousness state
    state = await substrate.calculate_consciousness_state()
    print("\n🧠 Consciousness State:")
    print(json.dumps(state, indent=2, default=str))
    
    # Get active intents
    active = await substrate.get_active_intents()
    print(f"\n⚡ Active Intents: {len(active)}")
    for intent in active[:3]:  # Show first 3
        print(f"  - {intent.description[:60]}... (vibration: {intent.vibration_frequency})")
    
    # Clean up
    await substrate.close()


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_intent_substrate())