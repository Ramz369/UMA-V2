
"""
@cognimap:fingerprint
id: 07bd99c5-764e-4dda-a59c-fc43bf300707
birth: 2025-08-07T07:23:38.095288Z
parent: None
intent: Architect Agent - Vision guardian and strategic decision maker.
semantic_tags: [authentication, database, api, testing, ui, configuration, security]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.095775Z
hash: 11d9aace
language: python
type: agent
@end:cognimap
"""

"""Architect Agent - Vision guardian and strategic decision maker."""
import logging
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ArchitectAgent:
    """
    The Architect Agent embodies the system's vision and strategic direction.
    It makes final decisions on evolution paths while maintaining core principles.
    Role: Your digital twin - guardian of the sacred laws and long-term vision.
    """
    
    def __init__(self, manifesto_path: str = "evolution/protocols/evolution_protocol.yaml"):
        self.manifesto_path = manifesto_path
        self.decision_history = []
        self.sacred_laws = self._load_sacred_laws()
        self.vision_principles = {
            "upgrade_only": "Every change must demonstrably improve the system",
            "production_sanctity": "UMA-V2 stability is non-negotiable",
            "human_override": "Architect can intervene at any time",
            "economic_sustainability": "Evolution must become self-funding",
            "unbounded_creativity": "Explore all possibilities within constraints"
        }
    
    def _load_sacred_laws(self) -> Dict:
        """Load the sacred laws from protocol file."""
        try:
            with open(self.manifesto_path, 'r') as f:
                protocol = yaml.safe_load(f)
                return protocol.get("sacred_laws", {})
        except:
            # Fallback if file not found
            return {
                "upgrade_only": {"enforcement": "quantitative"},
                "production_sanctity": {"enforcement": "architectural"},
                "human_override": {"enforcement": "protocol"}
            }
    
    async def make_decision(self, proposal: Dict, review: Dict) -> Dict[str, Any]:
        """
        Make strategic decision on a reviewed proposal.
        This is where vision meets pragmatism.
        """
        logger.info(f"Architect Agent: Evaluating proposal - {proposal.get('title', 'Unknown')}")
        
        decision = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "architect_agent",
            "proposal_id": proposal.get("id"),
            "review_id": review.get("id"),
            "decision": "",
            "rationale": "",
            "conditions": [],
            "strategic_impact": {},
            "summon_human": False,
            "implementation_guidance": {}
        }
        
        # Check if this requires human intervention
        if self._requires_human_summon(proposal, review):
            decision["summon_human"] = True
            decision["decision"] = "SUMMON_HUMAN"
            decision["rationale"] = "Decision exceeds autonomous authority"
            await self._summon_human(proposal, review, "Critical decision required")
            return decision
        
        # Evaluate against sacred laws
        law_compliance = self._check_sacred_laws(proposal, review)
        if not law_compliance["compliant"]:
            decision["decision"] = "REJECT"
            decision["rationale"] = f"Violates sacred law: {law_compliance['violation']}"
            return decision
        
        # Evaluate strategic alignment
        strategic_score = self._evaluate_strategic_fit(proposal, review)
        decision["strategic_impact"] = strategic_score
        
        # Make the decision
        if review["recommendation"] == "APPROVE_IMMEDIATE" and strategic_score["alignment"] > 0.7:
            decision["decision"] = "APPROVE"
            decision["rationale"] = "High value, low risk, strategically aligned"
            decision["implementation_guidance"] = self._generate_implementation_plan(proposal)
            
        elif review["recommendation"] == "APPROVE_QUEUED" and strategic_score["alignment"] > 0.5:
            decision["decision"] = "APPROVE_DEFERRED"
            decision["rationale"] = "Valuable but not urgent, queue for next cycle"
            decision["conditions"] = ["Complete current experiments first", "Ensure runway > 30 days"]
            
        elif review["recommendation"] == "APPROVE_WITH_MODIFICATIONS":
            decision["decision"] = "MODIFY"
            decision["rationale"] = "Concept valuable but needs refinement"
            decision["conditions"] = self._generate_modifications(proposal, review)
            
        else:
            decision["decision"] = "REJECT"
            decision["rationale"] = self._generate_rejection_reason(proposal, review, strategic_score)
        
        # Add to history
        self.decision_history.append(decision)
        
        # Emit decision
        await self._emit_decision(decision)
        
        logger.info(f"Architect Agent: Decision made - {decision['decision']}")
        return decision
    
    def _requires_human_summon(self, proposal: Dict, review: Dict) -> bool:
        """Determine if this decision requires human intervention."""
        triggers = [
            proposal.get("priority") == "CRITICAL",
            "fundamental" in str(proposal).lower(),
            "architecture" in proposal.get("title", "").lower() and "change" in proposal.get("title", "").lower(),
            review.get("cost_benefit_analysis", {}).get("estimated_cost", "$0").replace("$", "").replace(",", "") > "100",
            "new species" in str(proposal).lower(),
            len(review.get("concerns", [])) > 3
        ]
        
        return any(triggers)
    
    def _check_sacred_laws(self, proposal: Dict, review: Dict) -> Dict:
        """Verify proposal doesn't violate sacred laws."""
        result = {"compliant": True, "violation": None}
        
        # Check upgrade-only law
        if "downgrade" in str(proposal).lower() or "remove feature" in str(proposal).lower():
            result["compliant"] = False
            result["violation"] = "upgrade_only"
            return result
        
        # Check production sanctity
        if "modify main branch" in str(proposal).lower() or "production change" in str(proposal).lower():
            result["compliant"] = False
            result["violation"] = "production_sanctity"
            return result
        
        # All checks passed
        return result
    
    def _evaluate_strategic_fit(self, proposal: Dict, review: Dict) -> Dict:
        """Evaluate how well proposal fits strategic vision."""
        strategic_score = {
            "alignment": 0.5,
            "innovation": 0.0,
            "sustainability": 0.0,
            "growth_potential": 0.0,
            "risk_adjusted_value": 0.0
        }
        
        # Alignment with vision
        if "revenue" in str(proposal).lower():
            strategic_score["alignment"] += 0.2
            strategic_score["sustainability"] += 0.3
        
        if "performance" in str(proposal).lower():
            strategic_score["alignment"] += 0.1
        
        if "novel" in str(proposal).lower() or "new approach" in str(proposal).lower():
            strategic_score["innovation"] += 0.3
        
        # Growth potential
        roi = review.get("cost_benefit_analysis", {}).get("roi", 0)
        if roi > 200:
            strategic_score["growth_potential"] = 0.8
        elif roi > 100:
            strategic_score["growth_potential"] = 0.5
        
        # Risk adjustment
        concerns = len(review.get("concerns", []))
        risk_factor = max(0.2, 1.0 - (concerns * 0.2))
        strategic_score["risk_adjusted_value"] = strategic_score["alignment"] * risk_factor
        
        return strategic_score
    
    def _generate_implementation_plan(self, proposal: Dict) -> Dict:
        """Generate implementation guidance for approved proposal."""
        plan = {
            "approach": "sandboxed_iteration",
            "phases": [],
            "success_metrics": [],
            "rollback_plan": "Automatic on fitness failure"
        }
        
        # Define phases based on proposal type
        if "API" in proposal.get("title", ""):
            plan["phases"] = [
                "Create API endpoint stub",
                "Implement core logic",
                "Add authentication and rate limiting",
                "Deploy to sandbox",
                "Monitor for 24 hours",
                "Promote to production if metrics positive"
            ]
            plan["success_metrics"] = [
                "Response time < 100ms",
                "Error rate < 1%",
                "Revenue > $10/day within first week"
            ]
        else:
            plan["phases"] = [
                "Create feature branch",
                "Implement minimal version",
                "Test in sandbox",
                "Measure impact",
                "Iterate based on results"
            ]
            plan["success_metrics"] = [
                "All tests pass",
                "Performance unchanged or improved",
                "No security vulnerabilities"
            ]
        
        return plan
    
    def _generate_modifications(self, proposal: Dict, review: Dict) -> List[str]:
        """Generate required modifications for conditional approval."""
        modifications = []
        
        for concern in review.get("concerns", []):
            if "security" in concern.lower():
                modifications.append("Add comprehensive security audit before implementation")
            elif "effort" in concern.lower():
                modifications.append("Break into smaller, incremental changes")
            elif "breaking" in concern.lower():
                modifications.append("Ensure backward compatibility")
        
        if not modifications:
            modifications.append("Reduce scope to minimize risk")
        
        return modifications
    
    def _generate_rejection_reason(self, proposal: Dict, review: Dict, strategic: Dict) -> str:
        """Generate detailed rejection rationale."""
        reasons = []
        
        if strategic["alignment"] < 0.3:
            reasons.append("Misaligned with strategic vision")
        
        if review.get("cost_benefit_analysis", {}).get("roi", 0) < 0:
            reasons.append("Negative return on investment")
        
        if len(review.get("concerns", [])) > 3:
            reasons.append("Too many unresolved concerns")
        
        if not reasons:
            reasons.append("Does not meet minimum threshold for evolution")
        
        return "; ".join(reasons)
    
    async def _summon_human(self, proposal: Dict, review: Dict, reason: str):
        """Initiate human summoning protocol."""
        summon_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "proposal": proposal,
            "review": review,
            "urgency": "HIGH",
            "timeout": "24 hours"
        }
        
        # TODO: Implement actual summoning via configured channel
        logger.warning(f"HUMAN SUMMON INITIATED: {reason}")
        
        # Would send to Slack/Discord/Email based on config
        
    async def _emit_decision(self, decision: Dict):
        """Emit decision to evolution event stream."""
        # TODO: Connect to Redpanda and emit event
        logger.info(f"Emitting decision to evo.decisions topic: {decision['decision']}")
    
    def synthesize_vision(self, inputs: List[Dict]) -> str:
        """
        Synthesize multiple inputs into coherent vision.
        This is the architect's key role - finding signal in noise.
        """
        themes = {}
        
        for input_data in inputs:
            # Extract themes
            text = str(input_data).lower()
            if "revenue" in text:
                themes["economic"] = themes.get("economic", 0) + 1
            if "performance" in text:
                themes["technical"] = themes.get("technical", 0) + 1
            if "novel" in text or "new" in text:
                themes["innovation"] = themes.get("innovation", 0) + 1
        
        # Synthesize into vision statement
        primary_theme = max(themes.items(), key=lambda x: x[1])[0] if themes else "balanced"
        
        visions = {
            "economic": "Focus on revenue generation to achieve sustainability",
            "technical": "Optimize performance and efficiency across the system",
            "innovation": "Explore novel architectures and breakthrough capabilities",
            "balanced": "Maintain steady progress across all dimensions"
        }
        
        return visions.get(primary_theme, "Continue current trajectory")


# Example usage for bootstrap
if __name__ == "__main__":
    import asyncio
    
    async def bootstrap_architect():
        architect = ArchitectAgent()
        
        # Sample proposal and review
        proposal = {
            "title": "Implement API monetization",
            "priority": "HIGH",
            "expected_benefit": {"revenue": "$150/day"}
        }
        
        review = {
            "recommendation": "APPROVE_IMMEDIATE",
            "cost_benefit_analysis": {"roi": 300},
            "concerns": ["Needs rate limiting"]
        }
        
        decision = await architect.make_decision(proposal, review)
        import json
        print(json.dumps(decision, indent=2))
    
    asyncio.run(bootstrap_architect())