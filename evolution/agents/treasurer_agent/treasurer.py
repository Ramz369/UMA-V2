
"""
@cognimap:fingerprint
id: 80feed09-906e-42cc-8252-131456361d86
birth: 2025-08-07T07:23:38.096128Z
parent: None
intent: Treasurer Agent - Economic management and revenue generation.
semantic_tags: [api, service, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.096916Z
hash: 8940cfb5
language: python
type: agent
@end:cognimap
"""

"""Treasurer Agent - Economic management and revenue generation."""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TreasurerAgent:
    """
    The Treasurer Agent manages the evolution engine's economics.
    It tracks spending, generates revenue, and ensures financial sustainability.
    Role: The CFO of evolution - making it self-funding.
    """
    
    def __init__(self, wallet_path: str = "evolution/treasury/wallet.json"):
        self.wallet_path = wallet_path
        self.ledger_path = "evolution/treasury/ledger.yaml"
        self.treasury_data = self._load_treasury()
        self.revenue_streams = {}
        self.burn_rate_history = []
        
    def _load_treasury(self) -> Dict:
        """Load treasury data from wallet."""
        try:
            with open(self.wallet_path, 'r') as f:
                return json.load(f)
        except:
            # Initialize if not found
            return {
                "seed_budget": 0,
                "current_balance": 0,
                "total_revenue": 0,
                "total_expenses": 0,
                "initialized": datetime.utcnow().isoformat()
            }
    
    def _save_treasury(self):
        """Save treasury data to wallet."""
        Path(self.wallet_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.wallet_path, 'w') as f:
            json.dump(self.treasury_data, f, indent=2)
    
    async def initialize_treasury(self, seed_budget: float) -> Dict:
        """Initialize treasury with seed budget."""
        logger.info(f"Treasurer Agent: Initializing with seed budget ${seed_budget}")
        
        self.treasury_data["seed_budget"] = seed_budget
        self.treasury_data["current_balance"] = seed_budget
        self.treasury_data["initialized"] = datetime.utcnow().isoformat()
        
        self._save_treasury()
        
        # Record transaction
        await self._record_transaction(
            type="CREDIT",
            amount=seed_budget,
            description="Seed budget from architect",
            category="FUNDING"
        )
        
        return {
            "status": "initialized",
            "seed_budget": seed_budget,
            "runway": self._calculate_runway()
        }
    
    async def assess_financial_health(self) -> Dict[str, Any]:
        """Assess current financial health and priorities."""
        logger.info("Treasurer Agent: Assessing financial health")
        
        assessment = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "treasurer_agent",
            "balance": self.treasury_data["current_balance"],
            "burn_rate": self._calculate_burn_rate(),
            "runway_days": self._calculate_runway(),
            "revenue_rate": self._calculate_revenue_rate(),
            "priority_mode": "",
            "recommendations": [],
            "active_revenue_streams": [],
            "health_score": 0
        }
        
        # Determine priority mode based on runway
        runway = assessment["runway_days"]
        if runway < 7:
            assessment["priority_mode"] = "CRITICAL_REVENUE"
            assessment["recommendations"].append("Pause all non-revenue experiments immediately")
            assessment["recommendations"].append("Launch emergency revenue generation")
        elif runway < 30:
            assessment["priority_mode"] = "URGENT_REVENUE"
            assessment["recommendations"].append("Focus 80% resources on revenue generation")
        elif runway < 60:
            assessment["priority_mode"] = "BALANCED"
            assessment["recommendations"].append("Maintain 60/40 revenue/capability split")
        else:
            assessment["priority_mode"] = "CAPABILITY_GROWTH"
            assessment["recommendations"].append("Can afford capability investments")
        
        # Calculate health score
        assessment["health_score"] = self._calculate_health_score(assessment)
        
        # List active revenue streams
        assessment["active_revenue_streams"] = list(self.revenue_streams.keys())
        
        # Emit assessment
        await self._emit_assessment(assessment)
        
        return assessment
    
    def _calculate_burn_rate(self) -> float:
        """Calculate current burn rate ($/day)."""
        # Look at last 7 days of expenses
        recent_expenses = 0
        days = 7
        
        # Simplified calculation - would read from ledger in production
        # Assuming $10/day for compute and services
        base_burn = 10.0
        
        # Add cost of active experiments
        experiment_cost = len(self.revenue_streams) * 2.0
        
        return base_burn + experiment_cost
    
    def _calculate_runway(self) -> int:
        """Calculate runway in days."""
        burn_rate = self._calculate_burn_rate()
        if burn_rate == 0:
            return 999  # Infinite runway
        
        balance = self.treasury_data["current_balance"]
        runway_days = int(balance / burn_rate)
        
        return max(0, runway_days)
    
    def _calculate_revenue_rate(self) -> float:
        """Calculate current revenue rate ($/day)."""
        daily_revenue = 0
        
        for stream_name, stream_data in self.revenue_streams.items():
            if stream_data.get("status") == "active":
                daily_revenue += stream_data.get("daily_revenue", 0)
        
        return daily_revenue
    
    def _calculate_health_score(self, assessment: Dict) -> float:
        """Calculate overall financial health score (0-100)."""
        score = 50.0  # Base score
        
        # Runway factor (up to 30 points)
        runway = assessment["runway_days"]
        if runway > 90:
            score += 30
        elif runway > 60:
            score += 20
        elif runway > 30:
            score += 10
        elif runway < 7:
            score -= 20
        
        # Revenue factor (up to 30 points)
        revenue_rate = assessment["revenue_rate"]
        burn_rate = assessment["burn_rate"]
        if revenue_rate > burn_rate:
            score += 30
        elif revenue_rate > burn_rate * 0.5:
            score += 15
        elif revenue_rate > 0:
            score += 5
        
        # Growth factor (up to 20 points)
        if self.treasury_data["total_revenue"] > self.treasury_data["seed_budget"]:
            score += 20
        elif self.treasury_data["total_revenue"] > 0:
            score += 10
        
        return min(100, max(0, score))
    
    async def evaluate_investment(self, proposal: Dict) -> Dict[str, Any]:
        """Evaluate investment opportunity."""
        logger.info(f"Treasurer Agent: Evaluating investment - {proposal.get('title')}")
        
        evaluation = {
            "timestamp": datetime.utcnow().isoformat(),
            "proposal_id": proposal.get("id"),
            "can_afford": False,
            "recommended": False,
            "roi_estimate": 0,
            "payback_days": 999,
            "risk_assessment": "",
            "decision_rationale": ""
        }
        
        # Get investment cost
        cost_str = proposal.get("implementation_cost", "$0")
        cost = float(cost_str.replace("$", "").replace(",", "") if "$" in cost_str else 0)
        
        # Check if we can afford it
        balance = self.treasury_data["current_balance"]
        runway = self._calculate_runway()
        
        if cost > balance * 0.1:  # Don't spend more than 10% of treasury
            evaluation["can_afford"] = False
            evaluation["decision_rationale"] = "Investment exceeds 10% of treasury"
        elif runway < 30 and "revenue" not in str(proposal).lower():
            evaluation["can_afford"] = False
            evaluation["decision_rationale"] = "Low runway - only revenue investments allowed"
        else:
            evaluation["can_afford"] = True
        
        # Calculate ROI
        if "potential_revenue" in str(proposal):
            # Parse revenue (simplified)
            daily_revenue = 50  # Simplified parsing
            if cost > 0:
                evaluation["payback_days"] = cost / daily_revenue
                evaluation["roi_estimate"] = (daily_revenue * 30 / cost - 1) * 100
                
                if evaluation["roi_estimate"] > 200:
                    evaluation["recommended"] = True
                    evaluation["risk_assessment"] = "LOW"
                elif evaluation["roi_estimate"] > 100:
                    evaluation["recommended"] = True
                    evaluation["risk_assessment"] = "MEDIUM"
                else:
                    evaluation["risk_assessment"] = "HIGH"
        
        return evaluation
    
    async def launch_revenue_stream(self, stream_config: Dict) -> Dict:
        """Launch a new revenue stream."""
        logger.info(f"Treasurer Agent: Launching revenue stream - {stream_config.get('name')}")
        
        stream_name = stream_config.get("name", f"stream_{len(self.revenue_streams)}")
        
        self.revenue_streams[stream_name] = {
            "name": stream_name,
            "type": stream_config.get("type", "api"),
            "status": "launching",
            "launch_date": datetime.utcnow().isoformat(),
            "daily_revenue": 0,
            "total_revenue": 0,
            "customers": 0,
            "config": stream_config
        }
        
        # Simulate launch cost
        launch_cost = stream_config.get("launch_cost", 50)
        await self._record_transaction(
            type="INVESTMENT",
            amount=-launch_cost,
            description=f"Launch {stream_name}",
            category="REVENUE_INVESTMENT"
        )
        
        # Simulate initial success (would be real implementation in production)
        self.revenue_streams[stream_name]["status"] = "active"
        self.revenue_streams[stream_name]["daily_revenue"] = stream_config.get("expected_daily", 10)
        
        return {
            "status": "launched",
            "stream_name": stream_name,
            "expected_daily_revenue": self.revenue_streams[stream_name]["daily_revenue"]
        }
    
    async def collect_revenue(self) -> Dict:
        """Collect revenue from all active streams."""
        logger.info("Treasurer Agent: Collecting revenue")
        
        daily_collection = {
            "timestamp": datetime.utcnow().isoformat(),
            "streams": {},
            "total_collected": 0
        }
        
        for stream_name, stream_data in self.revenue_streams.items():
            if stream_data["status"] == "active":
                daily_revenue = stream_data["daily_revenue"]
                
                # Record collection
                daily_collection["streams"][stream_name] = daily_revenue
                daily_collection["total_collected"] += daily_revenue
                
                # Update stream totals
                stream_data["total_revenue"] += daily_revenue
                
                # Record transaction
                await self._record_transaction(
                    type="REVENUE",
                    amount=daily_revenue,
                    description=f"Daily revenue from {stream_name}",
                    category="REVENUE_COLLECTION"
                )
        
        # Update treasury
        self.treasury_data["current_balance"] += daily_collection["total_collected"]
        self.treasury_data["total_revenue"] += daily_collection["total_collected"]
        self._save_treasury()
        
        logger.info(f"Collected ${daily_collection['total_collected']} in revenue")
        return daily_collection
    
    async def pay_expenses(self, expense_type: str, amount: float, description: str) -> bool:
        """Pay an expense if affordable."""
        if amount > self.treasury_data["current_balance"]:
            logger.warning(f"Cannot afford expense: {description} (${amount})")
            return False
        
        await self._record_transaction(
            type="DEBIT",
            amount=-amount,
            description=description,
            category=expense_type
        )
        
        self.treasury_data["current_balance"] -= amount
        self.treasury_data["total_expenses"] += amount
        self._save_treasury()
        
        return True
    
    async def _record_transaction(self, type: str, amount: float, description: str, category: str):
        """Record transaction in ledger."""
        transaction = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": type,
            "amount": amount,
            "balance_after": self.treasury_data["current_balance"] + (amount if type != "DEBIT" else 0),
            "description": description,
            "category": category
        }
        
        # Would append to ledger file in production
        logger.info(f"Transaction: {type} ${abs(amount):.2f} - {description}")
    
    async def _emit_assessment(self, assessment: Dict):
        """Emit financial assessment to evolution event stream."""
        # TODO: Connect to Redpanda and emit event
        logger.info(f"Emitting assessment: Priority mode = {assessment['priority_mode']}")
    
    def generate_revenue_proposals(self) -> List[Dict]:
        """Generate proposals for new revenue streams."""
        proposals = []
        
        # API monetization
        if "semantic_diff_api" not in self.revenue_streams:
            proposals.append({
                "title": "Launch Semantic Diff API",
                "type": "api_service",
                "expected_daily": 50,
                "launch_cost": 100,
                "time_to_market": "3 days",
                "confidence": 0.8
            })
        
        # Tool marketplace
        if "tool_marketplace" not in self.revenue_streams:
            proposals.append({
                "title": "Create Tool Marketplace",
                "type": "marketplace",
                "expected_daily": 100,
                "launch_cost": 300,
                "time_to_market": "7 days",
                "confidence": 0.6
            })
        
        # Compute sharing
        if "compute_sharing" not in self.revenue_streams:
            proposals.append({
                "title": "Sell Unused Compute",
                "type": "compute",
                "expected_daily": 20,
                "launch_cost": 50,
                "time_to_market": "2 days",
                "confidence": 0.9
            })
        
        return proposals


# Example usage for bootstrap
if __name__ == "__main__":
    import asyncio
    
    async def bootstrap_treasury():
        treasurer = TreasurerAgent()
        
        # Initialize with seed budget
        await treasurer.initialize_treasury(1000)
        
        # Assess health
        health = await treasurer.assess_financial_health()
        print(f"Financial Health Score: {health['health_score']}")
        print(f"Runway: {health['runway_days']} days")
        print(f"Priority Mode: {health['priority_mode']}")
        
        # Generate revenue proposals
        proposals = treasurer.generate_revenue_proposals()
        print(f"\nRevenue Proposals: {len(proposals)}")
        for p in proposals:
            print(f"  - {p['title']}: ${p['expected_daily']}/day")
    
    asyncio.run(bootstrap_treasury())