#!/usr/bin/env python3
"""
@cognimap:fingerprint
id: 888bd125-d504-400f-9bd9-ee0c3e3cfff1
birth: 2025-08-07T07:23:38.083733Z
parent: None
intent: Evolution Orchestrator with Kafka Integration - Coordinates the daily evolution cycle.
semantic_tags: [api, testing, ui, utility, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.084408Z
hash: e922c6a0
language: python
type: component
@end:cognimap
"""

"""Evolution Orchestrator with Kafka Integration - Coordinates the daily evolution cycle."""
import asyncio
import logging
import yaml
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add parent paths for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import runtime and Kafka utilities
from runtime.agent_runtime import AgentSpawner, AgentRuntime
from common.kafka_utils import get_kafka, KafkaIntegration

# Import evolution agents
from agents.external_auditor.auditor import ExternalAuditor
from agents.discussion_agent.reviewer import DiscussionAgent
from agents.architect_agent.architect import ArchitectAgent
from agents.implementor_agent.implementor import ImplementorAgent
from agents.treasurer_agent.treasurer import TreasurerAgent

# Load environment variables
load_dotenv("evolution/.env.evolution")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class WiredEvolutionOrchestrator:
    """
    Evolution Orchestrator with full Kafka integration.
    Manages agent lifecycles and coordinates evolution cycles through message passing.
    """
    
    def __init__(self, config_path: str = "evolution/protocols/evolution_protocol.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Agent management
        self.spawner = AgentSpawner()
        self.agent_runtimes = {}
        
        # Kafka integration
        self.kafka = get_kafka()
        
        # Cycle tracking
        self.cycle_history = []
        self.active_cycle = None
        self.running = False
        
        # Load wallet for financial tracking
        self.wallet = self._load_wallet()
    
    def _load_config(self) -> Dict:
        """Load evolution protocol configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {"cycle": {"frequency": "daily"}}
    
    def _load_wallet(self) -> Dict:
        """Load wallet configuration."""
        try:
            import json
            with open("evolution/treasury/wallet.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load wallet: {e}")
            return {"balances": {"USD": 0}}
    
    async def initialize(self):
        """Initialize orchestrator and spawn all agents."""
        logger.info("=" * 60)
        logger.info("EVOLUTION ENGINE INITIALIZATION")
        logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        logger.info(f"Execution Venue: {os.getenv('EXECUTION_VENUE', 'local_docker')}")
        logger.info("=" * 60)
        
        # Start Kafka
        await self.kafka.start()
        health = await self.kafka.health_check()
        logger.info(f"Kafka status: {health['status']}")
        
        # Create orchestrator topics
        await self._setup_topics()
        
        # Spawn all evolution agents
        await self._spawn_agents()
        
        # Subscribe to agent outputs for coordination
        await self._setup_subscriptions()
        
        self.running = True
        logger.info("Evolution Engine initialized successfully")
        
        # Publish initialization event
        await self.kafka.publish_event("evolution-events", {
            "type": "engine_initialized",
            "timestamp": datetime.utcnow().isoformat(),
            "wallet_balance": self.wallet["balances"],
            "agents_spawned": list(self.agent_runtimes.keys())
        })
    
    async def _setup_topics(self):
        """Create necessary Kafka topics."""
        topics = [
            "evolution-events",
            "evolution-proposals", 
            "evolution-decisions",
            "evolution-implementations",
            "external-auditor-in", "external-auditor-out",
            "discussion-agent-in", "discussion-agent-out",
            "architect-agent-in", "architect-agent-out",
            "implementor-agent-in", "implementor-agent-out",
            "treasurer-agent-in", "treasurer-agent-out"
        ]
        
        # In production, would create topics via Kafka admin API
        # For now, topics auto-create on first use
        logger.info(f"Topics configured: {len(topics)}")
    
    async def _spawn_agents(self):
        """Spawn all evolution agents with runtime wrappers."""
        agents = [
            ("external-auditor", ExternalAuditor, {"credit_limit": int(os.getenv("CREDIT_LIMIT_AUDITOR", 500))}),
            ("discussion-agent", DiscussionAgent, {"credit_limit": int(os.getenv("CREDIT_LIMIT_REVIEWER", 300))}),
            ("architect-agent", ArchitectAgent, {"credit_limit": int(os.getenv("CREDIT_LIMIT_ARCHITECT", 1000))}),
            ("implementor-agent", ImplementorAgent, {"credit_limit": int(os.getenv("CREDIT_LIMIT_IMPLEMENTOR", 800))}),
            ("treasurer-agent", TreasurerAgent, {"credit_limit": int(os.getenv("CREDIT_LIMIT_TREASURER", 200))})
        ]
        
        for agent_id, agent_class, config in agents:
            try:
                runtime = await self.spawner.spawn_agent(agent_class, agent_id, config)
                self.agent_runtimes[agent_id] = runtime
                logger.info(f"Spawned agent: {agent_id}")
            except Exception as e:
                logger.error(f"Failed to spawn {agent_id}: {e}")
    
    async def _setup_subscriptions(self):
        """Subscribe to agent output topics for coordination."""
        # Subscribe to all agent outputs
        async def handle_agent_output(message):
            """Handle messages from agents."""
            agent = message.get("agent")
            msg_type = message.get("type")
            logger.debug(f"Received from {agent}: {msg_type}")
            
            # Store in cycle history
            if self.active_cycle:
                if "messages" not in self.active_cycle:
                    self.active_cycle["messages"] = []
                self.active_cycle["messages"].append(message)
        
        # Create consumer for all agent output topics
        agent_outputs = [f"{agent_id}-out" for agent_id in self.agent_runtimes.keys()]
        await self.kafka.create_consumer(
            agent_outputs,
            handle_agent_output,
            "orchestrator-consumer"
        )
        
        await self.kafka.start_consuming("orchestrator-consumer")
    
    async def run_evolution_cycle(self) -> Dict[str, Any]:
        """
        Run a complete evolution cycle using Kafka messaging.
        """
        logger.info("=" * 60)
        logger.info("EVOLUTION CYCLE STARTING")
        logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
        logger.info(f"Wallet Balance: ${self.wallet['balances'].get('USD', 0)}")
        logger.info("=" * 60)
        
        cycle_result = {
            "cycle_id": f"cycle_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.utcnow().isoformat(),
            "phases": {},
            "proposals_generated": 0,
            "proposals_approved": 0,
            "implementations_successful": 0,
            "revenue_impact": 0,
            "errors": [],
            "messages": []
        }
        
        self.active_cycle = cycle_result
        
        try:
            # Phase 0: Financial Assessment
            financial_health = await self._phase_financial_assessment()
            cycle_result["phases"]["financial"] = financial_health
            
            if financial_health["runway_days"] < 60:
                logger.warning(f"Low runway: {financial_health['runway_days']} days")
                await self._send_summon_alert("LOW_RUNWAY", financial_health)
            
            # Phase 1: External Audit via Kafka
            audit_result = await self._phase_audit_kafka()
            cycle_result["phases"]["audit"] = audit_result
            proposals = audit_result.get("proposals", [])
            cycle_result["proposals_generated"] = len(proposals)
            
            # Phase 2: Review Proposals via Kafka
            if proposals:
                reviews = await self._phase_review_kafka(proposals)
                cycle_result["phases"]["review"] = reviews
                
                # Phase 3: Architect Decisions via Kafka
                decisions = await self._phase_decide_kafka(proposals, reviews)
                cycle_result["phases"]["decisions"] = decisions
                
                # Phase 4: Implementation via Kafka
                approved = [p for p in proposals if decisions.get(p.get("id")) == "approved"]
                if approved:
                    implementations = await self._phase_implement_kafka(approved)
                    cycle_result["phases"]["implementation"] = implementations
                    cycle_result["implementations_successful"] = len(
                        [i for i in implementations if i.get("status") == "success"]
                    )
            
            # Phase 5: Treasury Update
            treasury_update = await self._phase_treasury_update()
            cycle_result["phases"]["treasury"] = treasury_update
            
            # Publish cycle completion
            await self.kafka.publish_event("evolution-events", {
                "type": "cycle_completed",
                "cycle_id": cycle_result["cycle_id"],
                "summary": {
                    "proposals": cycle_result["proposals_generated"],
                    "approved": cycle_result["proposals_approved"],
                    "implemented": cycle_result["implementations_successful"],
                    "duration": "calculated_later"
                }
            })
            
        except Exception as e:
            logger.error(f"Cycle error: {e}")
            cycle_result["errors"].append(str(e))
        
        self.cycle_history.append(cycle_result)
        self.active_cycle = None
        
        return cycle_result
    
    async def _phase_financial_assessment(self) -> Dict[str, Any]:
        """Assess financial health via treasurer agent."""
        # Send assessment request to treasurer
        request = {
            "type": "financial_assessment",
            "wallet": self.wallet["balances"],
            "burn_rate": self.wallet.get("burn_rate_daily", 10)
        }
        
        response = await self.kafka.request_reply(
            "treasurer-agent-in",
            "treasurer-agent-out",
            request,
            timeout=10.0
        )
        
        if response:
            return response.get("data", {})
        
        # Fallback calculation
        balance = self.wallet["balances"].get("USD", 0)
        burn_rate = self.wallet.get("burn_rate_daily", 10)
        runway = int(balance / burn_rate) if burn_rate > 0 else 999
        
        return {
            "balance": balance,
            "burn_rate": burn_rate,
            "runway_days": runway,
            "priority_mode": "CRITICAL_REVENUE" if runway < 30 else "NORMAL"
        }
    
    async def _phase_audit_kafka(self) -> Dict[str, Any]:
        """Run audit phase via Kafka messaging."""
        logger.info("Phase 1: External Audit (via Kafka)")
        
        # Send audit request to external auditor
        audit_request = {
            "type": "audit_request",
            "scope": "full_system",
            "focus_areas": ["performance", "efficiency", "revenue_opportunities"]
        }
        
        await self.kafka.publish_event("external-auditor-in", audit_request)
        
        # Wait for audit response (simplified - in production would use correlation ID)
        await asyncio.sleep(2)  # Give agent time to process
        
        # For now, return mock proposals
        return {
            "status": "completed",
            "proposals": [
                {
                    "id": "prop_001",
                    "title": "Optimize embedder performance",
                    "type": "optimization",
                    "estimated_impact": "20% faster processing"
                },
                {
                    "id": "prop_002", 
                    "title": "Add caching layer",
                    "type": "enhancement",
                    "estimated_impact": "Reduce API calls by 50%"
                }
            ]
        }
    
    async def _phase_review_kafka(self, proposals: List[Dict]) -> List[Dict]:
        """Review proposals via Kafka messaging."""
        logger.info("Phase 2: Review Proposals (via Kafka)")
        
        reviews = []
        for proposal in proposals:
            # Send review request to discussion agent
            review_request = {
                "type": "review_request",
                "proposal": proposal
            }
            
            await self.kafka.publish_event("discussion-agent-in", review_request)
            
            # Collect review (simplified)
            reviews.append({
                "proposal_id": proposal["id"],
                "recommendation": "approve",
                "risk_level": "low"
            })
        
        return reviews
    
    async def _phase_decide_kafka(self, proposals: List[Dict], reviews: List[Dict]) -> Dict[str, str]:
        """Make decisions via Kafka messaging."""
        logger.info("Phase 3: Architect Decisions (via Kafka)")
        
        decisions = {}
        for proposal in proposals:
            # Send decision request to architect
            decision_request = {
                "type": "decision_request",
                "proposal": proposal,
                "review": next((r for r in reviews if r["proposal_id"] == proposal["id"]), None)
            }
            
            await self.kafka.publish_event("architect-agent-in", decision_request)
            
            # Record decision (simplified)
            decisions[proposal["id"]] = "approved"
        
        return decisions
    
    async def _phase_implement_kafka(self, proposals: List[Dict]) -> List[Dict]:
        """Implement approved proposals via Kafka messaging."""
        logger.info("Phase 4: Implementation (via Kafka)")
        
        implementations = []
        for proposal in proposals:
            # Send implementation request to implementor
            impl_request = {
                "type": "implementation_request",
                "proposal": proposal
            }
            
            await self.kafka.publish_event("implementor-agent-in", impl_request)
            
            # Record implementation (simplified)
            implementations.append({
                "proposal_id": proposal["id"],
                "status": "success",
                "artifact": f"implementation_{proposal['id']}.py"
            })
        
        return implementations
    
    async def _phase_treasury_update(self) -> Dict[str, Any]:
        """Update treasury after cycle."""
        # Deduct daily burn rate
        self.wallet["balances"]["USD"] -= self.wallet.get("burn_rate_daily", 10)
        
        # Save updated wallet
        import json
        with open("evolution/treasury/wallet.json", 'w') as f:
            json.dump(self.wallet, f, indent=2)
        
        return {
            "new_balance": self.wallet["balances"]["USD"],
            "burn_today": self.wallet.get("burn_rate_daily", 10),
            "runway_days": int(self.wallet["balances"]["USD"] / self.wallet.get("burn_rate_daily", 10))
        }
    
    async def _send_summon_alert(self, urgency: str, data: Dict):
        """Send alert to summon channel."""
        summon_channel = os.getenv("SUMMON_CHANNEL", "you@example.com")
        
        alert = {
            "type": "summon_alert",
            "urgency": urgency,
            "channel": summon_channel,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.kafka.publish_event("evolution-events", alert)
        logger.warning(f"SUMMON ALERT sent to {summon_channel}: {urgency}")
    
    async def shutdown(self):
        """Shutdown orchestrator and all agents."""
        logger.info("Shutting down Evolution Engine...")
        
        self.running = False
        
        # Stop all agents
        await self.spawner.stop_all()
        
        # Stop Kafka
        await self.kafka.stop()
        
        logger.info("Evolution Engine shutdown complete")
    
    async def run_forever(self):
        """Run orchestrator continuously based on cadence."""
        logger.info("Evolution Engine running. Press Ctrl+C to stop.")
        
        while self.running:
            try:
                # Run evolution cycle
                await self.run_evolution_cycle()
                
                # Wait for next cycle (simplified - would use cron in production)
                logger.info("Cycle complete. Waiting for next cycle...")
                await asyncio.sleep(86400)  # Wait 24 hours
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Orchestrator error: {e}")
                await asyncio.sleep(60)  # Wait before retry


# CLI entry point
async def main():
    """Main entry point for wired orchestrator."""
    orchestrator = WiredEvolutionOrchestrator()
    
    try:
        # Initialize
        await orchestrator.initialize()
        
        # Check agent health
        health = await orchestrator.spawner.get_all_health()
        logger.info("Agent Health Status:")
        for agent_id, status in health.items():
            logger.info(f"  {agent_id}: {status['status']} (credits: {status['credits_used']}/{status['credit_limit']})")
        
        # Run one cycle for testing
        logger.info("\nRunning test evolution cycle...")
        result = await orchestrator.run_evolution_cycle()
        
        logger.info("\nCycle Results:")
        logger.info(f"  Proposals: {result['proposals_generated']}")
        logger.info(f"  Implementations: {result['implementations_successful']}")
        logger.info(f"  New Balance: ${result['phases'].get('treasury', {}).get('new_balance', 'N/A')}")
        
        # For continuous operation, uncomment:
        # await orchestrator.run_forever()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())