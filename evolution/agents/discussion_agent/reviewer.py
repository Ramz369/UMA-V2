
"""
@cognimap:fingerprint
id: 7eb5a2d8-916d-4cdc-b02b-e6c6c791b202
birth: 2025-08-07T07:23:38.096972Z
parent: None
intent: Discussion Agent - Pragmatic review and feasibility analysis.
semantic_tags: [database, api, ui, service, model, configuration, security]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.097386Z
hash: 7afdc0dc
language: python
type: agent
@end:cognimap
"""

"""Discussion Agent - Pragmatic review and feasibility analysis."""
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class DiscussionAgent:
    """
    The Discussion Agent provides pragmatic review of proposals.
    It evaluates feasibility, cost-benefit, and practical constraints.
    Role: Like ChatGPT-o3 in our 4-entity collaboration - the pragmatist.
    """
    
    def __init__(self, config_path: str = "evolution/protocols/economic_rules.yaml"):
        self.config_path = config_path
        self.review_history = []
        self.evaluation_criteria = {
            "technical_feasibility": 0.3,
            "economic_viability": 0.3,
            "risk_level": 0.2,
            "alignment_with_goals": 0.2
        }
    
    async def review_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review a proposal from the external auditor with pragmatic lens.
        """
        logger.info(f"Discussion Agent: Reviewing proposal - {proposal.get('title', 'Unknown')}")
        
        review = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "discussion_agent",
            "proposal_id": proposal.get("id"),
            "scores": {},
            "feasibility_assessment": {},
            "cost_benefit_analysis": {},
            "recommendation": "",
            "concerns": [],
            "quick_wins": []
        }
        
        # Score each criteria
        review["scores"] = self._score_proposal(proposal)
        
        # Detailed assessments
        review["feasibility_assessment"] = self._assess_feasibility(proposal)
        review["cost_benefit_analysis"] = self._analyze_cost_benefit(proposal)
        
        # Identify concerns and quick wins
        review["concerns"] = self._identify_concerns(proposal)
        review["quick_wins"] = self._identify_quick_wins(proposal)
        
        # Make recommendation
        review["recommendation"] = self._make_recommendation(review)
        
        # Store in history
        self.review_history.append(review)
        
        # Emit to evolution event stream
        await self._emit_review(review)
        
        logger.info(f"Discussion Agent: Review complete. Recommendation: {review['recommendation']}")
        return review
    
    def _score_proposal(self, proposal: Dict) -> Dict[str, float]:
        """Score proposal on multiple dimensions."""
        scores = {}
        
        # Technical feasibility
        if "implementation_cost" in str(proposal):
            cost = proposal.get("estimated_effort", "HIGH")
            scores["technical_feasibility"] = {
                "LOW": 0.9,
                "MEDIUM": 0.6,
                "HIGH": 0.3,
                "UNKNOWN": 0.5
            }.get(cost, 0.5)
        else:
            scores["technical_feasibility"] = 0.5
        
        # Economic viability
        if proposal.get("expected_benefit", {}).get("revenue"):
            revenue = proposal["expected_benefit"]["revenue"]
            if "$" in revenue:
                # Simple parsing - would be more sophisticated in production
                scores["economic_viability"] = 0.8 if "200" in revenue else 0.6
        else:
            scores["economic_viability"] = 0.3
        
        # Risk level (inverse - lower is better)
        priority = proposal.get("priority", "MEDIUM")
        scores["risk_level"] = {
            "LOW": 0.9,
            "MEDIUM": 0.6,
            "HIGH": 0.4,
            "CRITICAL": 0.2
        }.get(priority, 0.5)
        
        # Alignment with goals
        scores["alignment_with_goals"] = self._check_alignment(proposal)
        
        # Calculate weighted total
        total = sum(scores[k] * self.evaluation_criteria[k] for k in scores)
        scores["total"] = total
        
        return scores
    
    def _assess_feasibility(self, proposal: Dict) -> Dict:
        """Assess technical and practical feasibility."""
        feasibility = {
            "can_implement_now": False,
            "required_prerequisites": [],
            "estimated_time": "unknown",
            "confidence": 0.5
        }
        
        # Check if we can implement immediately
        effort = proposal.get("estimated_effort", "UNKNOWN")
        if effort == "LOW":
            feasibility["can_implement_now"] = True
            feasibility["estimated_time"] = "1-3 days"
            feasibility["confidence"] = 0.8
        elif effort == "MEDIUM":
            feasibility["can_implement_now"] = True
            feasibility["estimated_time"] = "3-7 days"
            feasibility["confidence"] = 0.6
        
        # Identify prerequisites
        if "API" in proposal.get("title", ""):
            feasibility["required_prerequisites"].append("API framework setup")
        if "parallel" in str(proposal).lower():
            feasibility["required_prerequisites"].append("Concurrency framework")
        
        return feasibility
    
    def _analyze_cost_benefit(self, proposal: Dict) -> Dict:
        """Perform cost-benefit analysis."""
        analysis = {
            "estimated_cost": "$0",
            "estimated_benefit": "$0",
            "payback_period": "unknown",
            "roi": 0,
            "recommendation": "neutral"
        }
        
        # Parse costs
        if "implementation_cost" in str(proposal):
            analysis["estimated_cost"] = "$100"  # Simplified
        
        # Parse benefits
        if "potential_revenue" in str(proposal):
            analysis["estimated_benefit"] = "$150/day"  # Simplified
            
        # Calculate ROI and payback
        if "$" in analysis["estimated_cost"] and "$" in analysis["estimated_benefit"]:
            # Simplified calculation
            cost = 100  # Parse from string in production
            daily_benefit = 150  # Parse from string in production
            analysis["payback_period"] = f"{cost/daily_benefit:.1f} days"
            analysis["roi"] = (daily_benefit * 30 / cost - 1) * 100  # 30-day ROI
            
            if analysis["roi"] > 200:
                analysis["recommendation"] = "strongly_positive"
            elif analysis["roi"] > 100:
                analysis["recommendation"] = "positive"
            elif analysis["roi"] > 0:
                analysis["recommendation"] = "neutral"
            else:
                analysis["recommendation"] = "negative"
        
        return analysis
    
    def _identify_concerns(self, proposal: Dict) -> List[str]:
        """Identify potential concerns with the proposal."""
        concerns = []
        
        # Check for red flags
        if proposal.get("priority") == "CRITICAL":
            concerns.append("High risk - needs careful implementation")
        
        if "security" in str(proposal).lower():
            concerns.append("Security implications need thorough review")
        
        if "breaking" in str(proposal).lower():
            concerns.append("May introduce breaking changes")
        
        effort = proposal.get("estimated_effort", "")
        if effort == "HIGH" or effort == "UNKNOWN":
            concerns.append("Implementation effort may be underestimated")
        
        return concerns
    
    def _identify_quick_wins(self, proposal: Dict) -> List[str]:
        """Identify quick win opportunities."""
        quick_wins = []
        
        # Look for easy improvements
        if proposal.get("estimated_effort") == "LOW":
            if "revenue" in str(proposal).lower():
                quick_wins.append("Low-effort revenue opportunity")
            if "performance" in str(proposal).lower():
                quick_wins.append("Easy performance gain")
        
        # Garbage flag was a perfect example
        if "cleanup" in str(proposal).lower() or "hygiene" in str(proposal).lower():
            quick_wins.append("Simple improvement with long-term benefits")
        
        return quick_wins
    
    def _check_alignment(self, proposal: Dict) -> float:
        """Check alignment with evolution goals."""
        alignment_score = 0.5  # Default neutral
        
        # Check against sacred laws
        if "upgrade" in str(proposal).lower():
            alignment_score += 0.2
        if "safety" in str(proposal).lower() or "sandbox" in str(proposal).lower():
            alignment_score += 0.1
        if "revenue" in str(proposal).lower():
            alignment_score += 0.2
        
        return min(alignment_score, 1.0)
    
    def _make_recommendation(self, review: Dict) -> str:
        """Make final recommendation based on review."""
        total_score = review["scores"]["total"]
        roi = review["cost_benefit_analysis"]["roi"]
        concerns = len(review["concerns"])
        quick_wins = len(review["quick_wins"])
        
        if total_score > 0.7 and roi > 100 and concerns < 2:
            return "APPROVE_IMMEDIATE"
        elif total_score > 0.6 and quick_wins > 0:
            return "APPROVE_QUEUED"
        elif total_score > 0.5 and concerns < 3:
            return "APPROVE_WITH_MODIFICATIONS"
        elif concerns > 3:
            return "REJECT_TOO_RISKY"
        else:
            return "DEFER_NEEDS_INFO"
    
    async def _emit_review(self, review: Dict):
        """Emit review to evolution event stream."""
        # TODO: Connect to Redpanda and emit event
        logger.info("Emitting review to evo.reviews topic")
    
    def pragmatic_filter(self, proposals: List[Dict]) -> List[Dict]:
        """
        Filter proposals through pragmatic lens.
        This is our key value - separating dreams from reality.
        """
        filtered = []
        
        for proposal in proposals:
            review = {
                "scores": self._score_proposal(proposal),
                "cost_benefit_analysis": self._analyze_cost_benefit(proposal)
            }
            
            # Only keep proposals that pass pragmatic thresholds
            if (review["scores"]["total"] > 0.5 and 
                review["cost_benefit_analysis"]["roi"] > 50):
                filtered.append(proposal)
        
        return sorted(filtered, key=lambda x: x.get("priority", ""), reverse=True)


# Example usage for bootstrap
if __name__ == "__main__":
    import asyncio
    
    async def bootstrap_review():
        reviewer = DiscussionAgent()
        
        # Sample proposal from external auditor
        proposal = {
            "title": "Monetize semantic diff as API",
            "description": "Package semantic diff tool as paid API service",
            "priority": "HIGH",
            "estimated_effort": "LOW",
            "expected_benefit": {
                "revenue": "$150/day",
                "performance": "neutral",
                "risk_reduction": "low"
            }
        }
        
        review = await reviewer.review_proposal(proposal)
        import json
        print(json.dumps(review, indent=2))
    
    asyncio.run(bootstrap_review())