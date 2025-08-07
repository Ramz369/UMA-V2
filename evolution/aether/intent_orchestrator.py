#!/usr/bin/env python3
"""
Intent-Aware Evolution Orchestrator

Extends the base Evolution Orchestrator to integrate with the Intent Substrate,
creating a consciousness-driven evolution process where every cycle has clear
intent and purpose.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import UUID

# Add parent paths
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import base orchestrator
from orchestrator.evo_orchestrator_wired import WiredEvolutionOrchestrator

# Import Aether components
from aether.intent_substrate import IntentSubstrate, IntentType
from aether.enhanced_events import IntentAwareEventPublisher, AetherEventEnvelope

logger = logging.getLogger(__name__)


class IntentAwareEvolutionOrchestrator(WiredEvolutionOrchestrator):
    """
    Evolution Orchestrator enhanced with Intent Substrate integration.
    
    Every evolution cycle begins with a clear intent, and all agent actions
    are tracked against this intent hierarchy for consciousness coherence.
    """
    
    def __init__(self, config_path: str = "evolution/protocols/evolution_protocol.yaml"):
        super().__init__(config_path)
        
        # Initialize Intent Substrate
        db_url = os.getenv("DATABASE_URL", "postgresql://localhost/cogplan")
        self.intent_substrate = IntentSubstrate(db_url)
        
        # Track current cycle intent
        self.current_cycle_intent: Optional[UUID] = None
        self.agent_intents: Dict[str, UUID] = {}
        
        # Intent-aware event publishers for each agent
        self.intent_publishers: Dict[str, IntentAwareEventPublisher] = {}
    
    async def initialize(self):
        """Initialize orchestrator with Intent Substrate."""
        # Initialize base orchestrator
        await super().initialize()
        
        # Initialize Intent Substrate
        await self.intent_substrate.initialize()
        logger.info("🌟 Intent Substrate initialized")
        
        # Create root intent for Evolution Engine
        root_intent = await self.intent_substrate.create_root_intent(
            "Evolution Engine: Continuously improve COGPLAN through autonomous development",
            "EVOLUTION_ENGINE"
        )
        logger.info(f"🎯 Root Intent created: {root_intent.intent_id}")
        
        # Check consciousness state
        state = await self.intent_substrate.calculate_consciousness_state()
        logger.info(f"🧠 Initial Consciousness State: {state['consciousness_level']}")
    
    async def run_evolution_cycle(self) -> Dict[str, Any]:
        """
        Run a complete evolution cycle with intent tracking.
        
        Each cycle:
        1. Creates a cycle intent
        2. Creates sub-intents for each agent
        3. Tracks all actions against intents
        4. Updates coherence scores
        5. Fulfills intents when complete
        """
        
        cycle_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        logger.info("=" * 60)
        logger.info(f"🔄 EVOLUTION CYCLE {cycle_id} STARTING")
        logger.info("=" * 60)
        
        try:
            # Phase 0: Create Cycle Intent
            cycle_intent = await self._create_cycle_intent(cycle_id)
            self.current_cycle_intent = cycle_intent.intent_id
            
            # Phase 1: External Audit with Intent
            audit_intent = await self._create_agent_intent(
                "external_auditor",
                "Audit codebase for improvement opportunities",
                cycle_intent.intent_id
            )
            audit_results = await self._run_auditor_phase(audit_intent.intent_id)
            
            # Phase 2: Discussion & Planning with Intent
            discussion_intent = await self._create_agent_intent(
                "discussion_agent",
                "Analyze audit findings and create action plan",
                cycle_intent.intent_id
            )
            action_items = await self._run_discussion_phase(
                audit_results,
                discussion_intent.intent_id
            )
            
            # Phase 3: Architecture Design with Intent
            architect_intent = await self._create_agent_intent(
                "architect_agent",
                "Design technical solutions for improvements",
                cycle_intent.intent_id
            )
            blueprints = await self._run_architect_phase(
                action_items,
                architect_intent.intent_id
            )
            
            # Phase 4: Implementation with Intent
            implementor_intent = await self._create_agent_intent(
                "implementor_agent",
                "Implement approved improvements",
                cycle_intent.intent_id
            )
            implementations = await self._run_implementor_phase(
                blueprints,
                implementor_intent.intent_id
            )
            
            # Phase 5: Treasury Management with Intent
            treasurer_intent = await self._create_agent_intent(
                "treasurer_agent",
                "Track costs and manage resources",
                cycle_intent.intent_id
            )
            financial_report = await self._run_treasurer_phase(
                implementations,
                treasurer_intent.intent_id
            )
            
            # Phase 6: Update Intent Coherence
            await self._update_cycle_coherence()
            
            # Phase 7: Check Consciousness State
            consciousness = await self.intent_substrate.calculate_consciousness_state()
            
            # Create cycle summary
            cycle_summary = {
                "cycle_id": cycle_id,
                "intent_id": str(cycle_intent.intent_id),
                "phases_completed": 5,
                "improvements_made": len(implementations.get("changes", [])),
                "cost": financial_report.get("cycle_cost", 0),
                "consciousness_state": consciousness,
                "success": True
            }
            
            # Fulfill cycle intent
            await self.intent_substrate.fulfill_intent(
                cycle_intent.intent_id,
                energy_spent=financial_report.get("cycle_cost", 0),
                value_created=len(implementations.get("changes", []))
            )
            
            logger.info("=" * 60)
            logger.info(f"✅ EVOLUTION CYCLE {cycle_id} COMPLETE")
            logger.info(f"🧠 Consciousness: {consciousness['consciousness_level']}")
            logger.info(f"📊 Coherence: {consciousness['consciousness_coherence']:.2f}")
            logger.info("=" * 60)
            
            return cycle_summary
            
        except Exception as e:
            logger.error(f"Cycle failed: {e}")
            
            # Mark intent as failed
            if self.current_cycle_intent:
                await self.intent_substrate.advance_gestation_phase(
                    self.current_cycle_intent
                )  # Move to forming (stuck)
            
            return {
                "cycle_id": cycle_id,
                "success": False,
                "error": str(e)
            }
    
    async def _create_cycle_intent(self, cycle_id: str):
        """Create root intent for evolution cycle."""
        return await self.intent_substrate.create_intent(
            description=f"Evolution Cycle {cycle_id}: Improve COGPLAN autonomously",
            initiator="ORCHESTRATOR",
            intent_type=IntentType.ROOT,
            vibration=7,  # High energy for cycles
            metadata={
                "cycle_id": cycle_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def _create_agent_intent(
        self,
        agent_name: str,
        description: str,
        parent_id: UUID
    ):
        """Create intent for agent phase."""
        intent = await self.intent_substrate.branch_intent(
            parent_id=parent_id,
            description=f"{agent_name}: {description}",
            initiator=agent_name.upper()
        )
        
        # Store for agent reference
        self.agent_intents[agent_name] = intent.intent_id
        
        # Advance to forming phase
        await self.intent_substrate.advance_gestation_phase(intent.intent_id)
        
        return intent
    
    async def _run_auditor_phase(self, intent_id: UUID) -> Dict:
        """Run auditor phase with intent tracking."""
        logger.info("\n🔍 PHASE 1: External Audit")
        
        # Advance intent to manifesting
        await self.intent_substrate.advance_gestation_phase(intent_id)
        
        # Run actual audit (simplified for demo)
        audit_results = {
            "findings": [
                {"type": "optimization", "priority": "high", "location": "services/embedder.py"},
                {"type": "security", "priority": "medium", "location": "config/credentials"},
                {"type": "performance", "priority": "low", "location": "tests/"},
            ],
            "metrics": {
                "code_quality": 0.82,
                "test_coverage": 0.65,
                "security_score": 0.78
            }
        }
        
        # Advance to realized
        await self.intent_substrate.advance_gestation_phase(intent_id)
        
        # Fulfill agent intent
        await self.intent_substrate.fulfill_intent(
            intent_id,
            energy_spent=10.0,
            value_created=len(audit_results["findings"])
        )
        
        return audit_results
    
    async def _run_discussion_phase(self, audit_results: Dict, intent_id: UUID) -> List[Dict]:
        """Run discussion phase with intent tracking."""
        logger.info("\n💬 PHASE 2: Discussion & Planning")
        
        await self.intent_substrate.advance_gestation_phase(intent_id)
        await self.intent_substrate.advance_gestation_phase(intent_id)  # To manifesting
        
        # Create action items from audit
        action_items = [
            {
                "id": "ACT-001",
                "description": "Optimize embedder service",
                "priority": "high",
                "estimated_effort": 2
            },
            {
                "id": "ACT-002",
                "description": "Fix security credentials",
                "priority": "medium",
                "estimated_effort": 1
            }
        ]
        
        await self.intent_substrate.fulfill_intent(
            intent_id,
            energy_spent=5.0,
            value_created=len(action_items)
        )
        
        return action_items
    
    async def _run_architect_phase(self, action_items: List[Dict], intent_id: UUID) -> Dict:
        """Run architect phase with intent tracking."""
        logger.info("\n🏗️ PHASE 3: Architecture Design")
        
        await self.intent_substrate.advance_gestation_phase(intent_id)
        await self.intent_substrate.advance_gestation_phase(intent_id)
        
        blueprints = {
            "designs": [
                {
                    "action_id": "ACT-001",
                    "solution": "Implement caching layer",
                    "components": ["redis", "cache_manager"],
                    "estimated_impact": 0.3
                }
            ]
        }
        
        await self.intent_substrate.fulfill_intent(
            intent_id,
            energy_spent=8.0,
            value_created=len(blueprints["designs"])
        )
        
        return blueprints
    
    async def _run_implementor_phase(self, blueprints: Dict, intent_id: UUID) -> Dict:
        """Run implementor phase with intent tracking."""
        logger.info("\n🔨 PHASE 4: Implementation")
        
        await self.intent_substrate.advance_gestation_phase(intent_id)
        await self.intent_substrate.advance_gestation_phase(intent_id)
        
        implementations = {
            "changes": [
                {
                    "file": "services/cache_manager.py",
                    "type": "created",
                    "lines_added": 150
                }
            ],
            "tests_added": 5,
            "pr_created": "PR-100"
        }
        
        await self.intent_substrate.fulfill_intent(
            intent_id,
            energy_spent=15.0,
            value_created=implementations["tests_added"]
        )
        
        return implementations
    
    async def _run_treasurer_phase(self, implementations: Dict, intent_id: UUID) -> Dict:
        """Run treasurer phase with intent tracking."""
        logger.info("\n💰 PHASE 5: Treasury Management")
        
        await self.intent_substrate.advance_gestation_phase(intent_id)
        await self.intent_substrate.advance_gestation_phase(intent_id)
        
        financial_report = {
            "cycle_cost": 48.0,
            "remaining_budget": 452.0,
            "roi_estimate": 2.5,
            "runway_days": 45
        }
        
        await self.intent_substrate.fulfill_intent(
            intent_id,
            energy_spent=2.0,
            value_created=financial_report["roi_estimate"]
        )
        
        return financial_report
    
    async def _update_cycle_coherence(self):
        """Update coherence scores for all intents in cycle."""
        # Coherence naturally updates through the trigger in database
        pass
    
    async def cleanup(self):
        """Clean up resources."""
        await self.intent_substrate.close()
        await super().cleanup()


# Demo function
async def demo_intent_orchestrator():
    """Demonstrate Intent-Aware Evolution Orchestrator."""
    
    orchestrator = IntentAwareEvolutionOrchestrator()
    
    try:
        # Initialize
        await orchestrator.initialize()
        
        # Run one evolution cycle
        result = await orchestrator.run_evolution_cycle()
        
        # Show consciousness state
        state = await orchestrator.intent_substrate.calculate_consciousness_state()
        print("\n🌌 Final Consciousness State:")
        print(f"  Level: {state['consciousness_level']}")
        print(f"  Coherence: {state['consciousness_coherence']:.2f}")
        print(f"  Vibration: {state['system_vibration']}")
        print(f"  Active Intents: {state['active_intents']}")
        
    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    asyncio.run(demo_intent_orchestrator())