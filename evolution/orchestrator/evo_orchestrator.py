
"""
@cognimap:fingerprint
id: 50c3ca98-21ee-44e2-85cd-af63d7d36215
birth: 2025-08-07T07:23:38.084517Z
parent: None
intent: Evolution Orchestrator - Coordinates the daily evolution cycle.
semantic_tags: [ui, model, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.085151Z
hash: 22f9a6dc
language: python
type: component
@end:cognimap
"""

"""Evolution Orchestrator - Coordinates the daily evolution cycle."""
import asyncio
import logging
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import evolution agents
import sys
sys.path.append(str(Path(__file__).parent.parent))

from agents.external_auditor.auditor import ExternalAuditor
from agents.discussion_agent.reviewer import DiscussionAgent
from agents.architect_agent.architect import ArchitectAgent
from agents.implementor_agent.implementor import ImplementorAgent
from agents.treasurer_agent.treasurer import TreasurerAgent

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class EvolutionOrchestrator:
    """
    The Evolution Orchestrator coordinates the daily evolution cycle.
    It manages the 4-entity review process and ensures all agents work in harmony.
    This is the conductor of the evolution symphony.
    """
    
    def __init__(self, config_path: str = "evolution/protocols/evolution_protocol.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize all agents
        self.auditor = ExternalAuditor()
        self.reviewer = DiscussionAgent()
        self.architect = ArchitectAgent()
        self.implementor = ImplementorAgent()
        self.treasurer = TreasurerAgent()
        
        self.cycle_history = []
        self.active_cycle = None
    
    def _load_config(self) -> Dict:
        """Load evolution protocol configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {"cycle": {"frequency": "daily"}}
    
    async def run_evolution_cycle(self) -> Dict[str, Any]:
        """
        Run a complete evolution cycle.
        This is the main loop that drives system evolution.
        """
        logger.info("=" * 60)
        logger.info("EVOLUTION CYCLE STARTING")
        logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
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
            "human_summons": 0
        }
        
        self.active_cycle = cycle_result
        
        try:
            # Phase 0: Financial Assessment
            financial_health = await self._phase_financial_assessment()
            cycle_result["phases"]["financial"] = financial_health
            
            # Determine if we should proceed based on financial health
            if financial_health["priority_mode"] == "CRITICAL_REVENUE":
                logger.warning("Critical financial state - focusing on revenue only")
                proposals = await self._generate_revenue_proposals()
            else:
                # Phase 1: External Audit
                audit_result = await self._phase_audit()
                cycle_result["phases"]["audit"] = audit_result
                proposals = audit_result.get("proposals", [])
            
            cycle_result["proposals_generated"] = len(proposals)
            
            # Phase 2: Review Proposals
            reviews = await self._phase_review(proposals)
            cycle_result["phases"]["review"] = reviews
            
            # Phase 3: Architect Decisions
            decisions = await self._phase_decide(proposals, reviews)
            cycle_result["phases"]["decisions"] = decisions
            
            # Count approvals and human summons
            for decision in decisions:
                if decision.get("decision") == "APPROVE":
                    cycle_result["proposals_approved"] += 1
                if decision.get("summon_human"):
                    cycle_result["human_summons"] += 1
            
            # Phase 4: Implementation
            if cycle_result["proposals_approved"] > 0:
                implementations = await self._phase_implement(decisions, proposals)
                cycle_result["phases"]["implementation"] = implementations
                
                for impl in implementations:
                    if impl.get("implementation_status") == "SUCCESS":
                        cycle_result["implementations_successful"] += 1
            
            # Phase 5: Revenue Collection
            if financial_health["active_revenue_streams"]:
                revenue = await self.treasurer.collect_revenue()
                cycle_result["revenue_impact"] = revenue.get("total_collected", 0)
            
        except Exception as e:
            logger.error(f"Cycle error: {e}")
            cycle_result["errors"].append(str(e))
        
        finally:
            cycle_result["end_time"] = datetime.utcnow().isoformat()
            self.cycle_history.append(cycle_result)
            self.active_cycle = None
            
            # Generate summary
            await self._generate_cycle_summary(cycle_result)
        
        logger.info("=" * 60)
        logger.info("EVOLUTION CYCLE COMPLETE")
        logger.info(f"Proposals: {cycle_result['proposals_generated']} generated, "
                   f"{cycle_result['proposals_approved']} approved")
        logger.info(f"Implementations: {cycle_result['implementations_successful']} successful")
        logger.info(f"Revenue Impact: ${cycle_result['revenue_impact']}")
        logger.info("=" * 60)
        
        return cycle_result
    
    async def _phase_financial_assessment(self) -> Dict:
        """Phase 0: Assess financial health."""
        logger.info("\n>>> PHASE 0: Financial Assessment")
        
        assessment = await self.treasurer.assess_financial_health()
        
        logger.info(f"Balance: ${assessment['balance']}")
        logger.info(f"Runway: {assessment['runway_days']} days")
        logger.info(f"Priority Mode: {assessment['priority_mode']}")
        logger.info(f"Health Score: {assessment['health_score']}/100")
        
        return assessment
    
    async def _phase_audit(self) -> Dict:
        """Phase 1: External audit of the system."""
        logger.info("\n>>> PHASE 1: External Audit")
        
        audit = await self.auditor.analyze_system()
        
        logger.info(f"Findings: {len(audit.get('findings', []))}")
        logger.info(f"Proposals: {len(audit.get('proposals', []))}")
        
        return audit
    
    async def _phase_review(self, proposals: List[Dict]) -> List[Dict]:
        """Phase 2: Review proposals."""
        logger.info(f"\n>>> PHASE 2: Review ({len(proposals)} proposals)")
        
        reviews = []
        for proposal in proposals:
            logger.info(f"Reviewing: {proposal.get('title', 'Unknown')}")
            review = await self.reviewer.review_proposal(proposal)
            reviews.append(review)
            logger.info(f"  Recommendation: {review['recommendation']}")
        
        return reviews
    
    async def _phase_decide(self, proposals: List[Dict], reviews: List[Dict]) -> List[Dict]:
        """Phase 3: Architect decisions."""
        logger.info(f"\n>>> PHASE 3: Architect Decisions")
        
        decisions = []
        for proposal, review in zip(proposals, reviews):
            logger.info(f"Deciding on: {proposal.get('title', 'Unknown')}")
            decision = await self.architect.make_decision(proposal, review)
            decisions.append(decision)
            logger.info(f"  Decision: {decision['decision']}")
            if decision.get("summon_human"):
                logger.warning("  🚨 HUMAN SUMMON REQUIRED")
        
        return decisions
    
    async def _phase_implement(self, decisions: List[Dict], proposals: List[Dict]) -> List[Dict]:
        """Phase 4: Implementation of approved changes."""
        logger.info(f"\n>>> PHASE 4: Implementation")
        
        implementations = []
        proposal_map = {p.get("id", i): p for i, p in enumerate(proposals)}
        
        for decision in decisions:
            if decision.get("decision") == "APPROVE":
                proposal = proposal_map.get(decision.get("proposal_id"), {})
                logger.info(f"Implementing: {proposal.get('title', 'Unknown')}")
                
                result = await self.implementor.implement_change(decision, proposal)
                implementations.append(result)
                
                logger.info(f"  Status: {result['implementation_status']}")
                if result.get("fitness_metrics"):
                    logger.info(f"  Fitness: {result['fitness_metrics'].get('overall_fitness', 0):.2f}")
        
        return implementations
    
    async def _generate_revenue_proposals(self) -> List[Dict]:
        """Generate emergency revenue proposals when runway is critical."""
        logger.info("Generating emergency revenue proposals")
        
        proposals = self.treasurer.generate_revenue_proposals()
        
        # Add urgency markers
        for proposal in proposals:
            proposal["priority"] = "CRITICAL"
            proposal["description"] = f"URGENT REVENUE: {proposal.get('title')}"
        
        return proposals
    
    async def _generate_cycle_summary(self, cycle_result: Dict):
        """Generate and save cycle summary."""
        summary_path = Path(f"evolution/reports/daily/cycle_{datetime.utcnow().strftime('%Y%m%d')}.md")
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        summary = f"""# Evolution Cycle Summary
Date: {cycle_result['start_time']}
Cycle ID: {cycle_result['cycle_id']}

## Metrics
- Proposals Generated: {cycle_result['proposals_generated']}
- Proposals Approved: {cycle_result['proposals_approved']}
- Successful Implementations: {cycle_result['implementations_successful']}
- Revenue Impact: ${cycle_result['revenue_impact']}
- Human Summons: {cycle_result['human_summons']}

## Financial Status
- Priority Mode: {cycle_result['phases'].get('financial', {}).get('priority_mode', 'Unknown')}
- Runway: {cycle_result['phases'].get('financial', {}).get('runway_days', 'Unknown')} days
- Health Score: {cycle_result['phases'].get('financial', {}).get('health_score', 0)}/100

## Errors
{cycle_result['errors'] if cycle_result['errors'] else 'None'}

---
*Generated by Evolution Orchestrator*
"""
        
        summary_path.write_text(summary)
        logger.info(f"Cycle summary saved to {summary_path}")
    
    async def bootstrap_evolution(self, seed_budget: float = 1000):
        """Bootstrap the evolution system with initial configuration."""
        logger.info("=" * 60)
        logger.info("BOOTSTRAPPING EVOLUTION SYSTEM")
        logger.info("=" * 60)
        
        # Initialize treasury
        logger.info(f"Initializing treasury with ${seed_budget} seed budget")
        await self.treasurer.initialize_treasury(seed_budget)
        
        # Run initial audit
        logger.info("Running initial system audit")
        audit = await self.auditor.analyze_system()
        logger.info(f"Initial findings: {len(audit.get('findings', []))} issues identified")
        
        # Check financial health
        health = await self.treasurer.assess_financial_health()
        logger.info(f"Initial runway: {health['runway_days']} days")
        
        logger.info("\nEvolution system bootstrapped successfully!")
        logger.info("Ready to begin evolution cycles")
        
        return {
            "status": "bootstrapped",
            "seed_budget": seed_budget,
            "initial_runway": health['runway_days'],
            "initial_findings": len(audit.get('findings', []))
        }


# Main execution
async def main():
    """Main entry point for evolution orchestrator."""
    orchestrator = EvolutionOrchestrator()
    
    # Check if bootstrapping is needed
    if not Path("evolution/treasury/wallet.json").exists():
        # Bootstrap with default seed budget (would get from user input)
        await orchestrator.bootstrap_evolution(seed_budget=1000)
    
    # Run evolution cycle
    result = await orchestrator.run_evolution_cycle()
    
    return result


if __name__ == "__main__":
    # Run the orchestrator
    asyncio.run(main())