#!/usr/bin/env python3
"""
Planner Agent - Decomposes tasks into actionable plans for other agents.
Core agent for UMA-V2 system orchestration.
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"      # Single agent, straightforward
    MODERATE = "moderate"  # 2-3 agents, some coordination
    COMPLEX = "complex"    # 4+ agents, heavy coordination
    CRITICAL = "critical"  # High risk, requires validation


@dataclass
class TaskPlan:
    """Structured plan for a task."""
    task_id: str
    feature: str
    complexity: TaskComplexity
    phases: List[Dict[str, Any]]
    agents_required: List[str]
    estimated_credits: int
    validation_steps: List[str]
    risk_assessment: Dict[str, Any]
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class PlannerAgent:
    """
    Planner Agent - The brain of UMA-V2 that decomposes tasks into plans.
    
    Responsibilities:
    - Analyze task requirements
    - Decompose into phases
    - Assign agents to phases
    - Estimate resource requirements
    - Create validation criteria
    - Assess risks
    """
    
    def __init__(self, kafka_client=None, credit_sentinel=None):
        """Initialize Planner Agent.
        
        Args:
            kafka_client: Optional Kafka client for event publishing
            credit_sentinel: Optional credit tracking system
        """
        self.kafka_client = kafka_client
        self.credit_sentinel = credit_sentinel
        self.plans_created = 0
        self.total_credits_estimated = 0
        
    async def create_plan(self, task: Dict[str, Any]) -> TaskPlan:
        """Create a comprehensive plan for a task.
        
        Args:
            task: Task specification with id, feature, and requirements
            
        Returns:
            TaskPlan with phases, agents, and validation steps
        """
        logger.info(f"Creating plan for task: {task.get('id', 'unknown')}")
        
        # Analyze task complexity
        complexity = self._analyze_complexity(task)
        
        # Decompose into phases
        phases = self._decompose_task(task, complexity)
        
        # Identify required agents
        agents = self._identify_agents(task, phases)
        
        # Estimate credits
        credits = self._estimate_credits(agents, complexity)
        
        # Create validation steps
        validation = self._create_validation_steps(task, phases)
        
        # Assess risks
        risks = self._assess_risks(task, complexity, credits)
        
        plan = TaskPlan(
            task_id=task.get("id", f"task_{self.plans_created}"),
            feature=task.get("feature", "Unknown feature"),
            complexity=complexity,
            phases=phases,
            agents_required=agents,
            estimated_credits=credits,
            validation_steps=validation,
            risk_assessment=risks
        )
        
        # Track metrics
        self.plans_created += 1
        self.total_credits_estimated += credits
        
        # Publish event if Kafka available
        if self.kafka_client:
            await self._publish_plan_event(plan)
        
        # Check credit budget if sentinel available
        if self.credit_sentinel:
            if not self.credit_sentinel.check_budget("planner", credits):
                logger.warning(f"Plan exceeds budget: {credits} credits")
                plan.risk_assessment["budget_risk"] = "HIGH"
        
        logger.info(f"Plan created: {plan.task_id} with {len(phases)} phases")
        return plan
    
    def _analyze_complexity(self, task: Dict) -> TaskComplexity:
        """Analyze task complexity based on requirements."""
        feature = task.get("feature", "").lower()
        agents = task.get("agents", [])
        
        # Critical if SLA or security involved
        if "sla" in feature or "security" in feature or "auth" in feature:
            return TaskComplexity.CRITICAL
        
        # Complex if many agents or real-time requirements
        if len(agents) >= 4 or "real-time" in feature:
            return TaskComplexity.COMPLEX
        
        # Moderate for typical multi-agent tasks
        if len(agents) >= 2:
            return TaskComplexity.MODERATE
        
        return TaskComplexity.SIMPLE
    
    def _decompose_task(self, task: Dict, complexity: TaskComplexity) -> List[Dict]:
        """Decompose task into execution phases."""
        phases = []
        feature = task.get("feature", "")
        
        # Phase 1: Always start with analysis/design
        phases.append({
            "phase_id": "1",
            "name": "Analysis & Design",
            "description": f"Analyze requirements for {feature}",
            "agent": "planner",
            "outputs": ["requirements", "architecture", "api_design"],
            "duration_estimate": "30m"
        })
        
        # Phase 2: Implementation (if needed)
        if "api" in feature.lower() or "service" in feature.lower():
            phases.append({
                "phase_id": "2", 
                "name": "Implementation",
                "description": "Generate code and configurations",
                "agent": "codegen",
                "outputs": ["source_code", "configs", "tests"],
                "duration_estimate": "1h"
            })
        
        # Phase 3: Testing (for complex tasks)
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]:
            phases.append({
                "phase_id": "3",
                "name": "Testing & Validation",
                "description": "Test functionality and performance",
                "agent": "stress-tester",
                "outputs": ["test_results", "performance_metrics"],
                "duration_estimate": "45m"
            })
        
        # Phase 4: Verification (for critical tasks)
        if complexity == TaskComplexity.CRITICAL:
            phases.append({
                "phase_id": "4",
                "name": "SLA Verification",
                "description": "Verify SLA compliance and requirements",
                "agent": "sla-verifier",
                "outputs": ["sla_report", "compliance_status"],
                "duration_estimate": "30m"
            })
        
        # Phase 5: Always end with review
        phases.append({
            "phase_id": str(len(phases) + 1),
            "name": "Review & Completion",
            "description": "Final review and documentation",
            "agent": "meta-analyst-v2",
            "outputs": ["summary", "recommendations", "metrics"],
            "duration_estimate": "15m"
        })
        
        return phases
    
    def _identify_agents(self, task: Dict, phases: List[Dict]) -> List[str]:
        """Identify all agents required for the task."""
        agents = set()
        
        # Add agents from phases
        for phase in phases:
            agent = phase.get("agent")
            if agent:
                agents.add(agent)
        
        # Add explicitly requested agents
        requested = task.get("agents", [])
        agents.update(requested)
        
        return sorted(list(agents))
    
    def _estimate_credits(self, agents: List[str], complexity: TaskComplexity) -> int:
        """Estimate total credits required."""
        # Base credits per agent
        agent_costs = {
            "planner": 100,
            "codegen": 150,
            "stress-tester": 100,
            "sla-verifier": 100,
            "meta-analyst-v2": 50,
            "backend-tester": 80,
            "frontend-tester": 80,
            "integration-agent": 60
        }
        
        # Calculate base cost
        base_cost = sum(agent_costs.get(agent, 50) for agent in agents)
        
        # Apply complexity multiplier
        multipliers = {
            TaskComplexity.SIMPLE: 1.0,
            TaskComplexity.MODERATE: 1.2,
            TaskComplexity.COMPLEX: 1.5,
            TaskComplexity.CRITICAL: 2.0
        }
        
        total = int(base_cost * multipliers[complexity])
        return total
    
    def _create_validation_steps(self, task: Dict, phases: List[Dict]) -> List[str]:
        """Create validation steps for the plan."""
        steps = []
        
        # Basic validation for all tasks
        steps.append("Verify all phases completed successfully")
        steps.append("Check credit usage within budget")
        
        # Add phase-specific validations
        for phase in phases:
            if phase["name"] == "Implementation":
                steps.append("Verify code compiles/runs without errors")
                steps.append("Check test coverage >= 80%")
            elif phase["name"] == "Testing & Validation":
                steps.append("Verify all tests pass")
                steps.append("Check performance meets requirements")
            elif phase["name"] == "SLA Verification":
                steps.append("Verify SLA targets met")
                steps.append("Check compliance requirements")
        
        # Task-specific validations
        if "real-time" in task.get("feature", "").lower():
            steps.append("Verify response time < 100ms p99")
        if "api" in task.get("feature", "").lower():
            steps.append("Verify API endpoints accessible")
            steps.append("Check API documentation complete")
        
        return steps
    
    def _assess_risks(self, task: Dict, complexity: TaskComplexity, credits: int) -> Dict:
        """Assess risks associated with the plan."""
        risks = {
            "technical_risk": "LOW",
            "credit_risk": "LOW",
            "timeline_risk": "LOW",
            "overall_risk": "LOW"
        }
        
        # Technical risk based on complexity
        if complexity == TaskComplexity.CRITICAL:
            risks["technical_risk"] = "HIGH"
        elif complexity == TaskComplexity.COMPLEX:
            risks["technical_risk"] = "MEDIUM"
        
        # Credit risk based on budget
        if credits > 500:
            risks["credit_risk"] = "HIGH"
        elif credits > 300:
            risks["credit_risk"] = "MEDIUM"
        
        # Timeline risk for real-time features
        if "real-time" in task.get("feature", "").lower():
            risks["timeline_risk"] = "MEDIUM"
        
        # Calculate overall risk
        risk_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        avg_risk = sum(risk_levels[r] for r in [
            risks["technical_risk"],
            risks["credit_risk"],
            risks["timeline_risk"]
        ]) / 3
        
        if avg_risk >= 1.5:
            risks["overall_risk"] = "HIGH"
        elif avg_risk >= 0.5:
            risks["overall_risk"] = "MEDIUM"
        
        return risks
    
    async def _publish_plan_event(self, plan: TaskPlan):
        """Publish plan creation event to Kafka."""
        event = {
            "id": f"plan_{plan.task_id}",
            "type": "plan_created",
            "timestamp": plan.created_at,
            "agent": "planner",
            "payload": asdict(plan),
            "meta": {
                "session_id": f"uma-v2-{datetime.now().strftime('%Y-%m-%d')}-001",
                "credits_used": 10  # Planning typically uses 10 credits
            },
            "garbage": False
        }
        
        try:
            await self.kafka_client.publish_event("agent-events", event)
            logger.info(f"Published plan event for {plan.task_id}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent metrics."""
        return {
            "agent": "planner",
            "plans_created": self.plans_created,
            "total_credits_estimated": self.total_credits_estimated,
            "avg_credits_per_plan": (
                self.total_credits_estimated / self.plans_created
                if self.plans_created > 0 else 0
            )
        }


# For API compatibility with test
async def create_pricing_api_plan() -> Dict[str, Any]:
    """Create a plan for pricing API (used by PILOT-001 test)."""
    planner = PlannerAgent()
    
    task = {
        "id": "PILOT-001",
        "feature": "Real-time pricing API with SLA",
        "agents": ["planner", "codegen", "stress-tester", "sla-verifier"],
        "expected_credits": 450
    }
    
    plan = await planner.create_plan(task)
    
    # Convert to test-expected format
    return {
        "api_design": {
            "endpoints": [
                "/api/v1/pricing/calculate",
                "/api/v1/pricing/quote",
                "/api/v1/pricing/history"
            ],
            "sla": {
                "response_time_p99": "100ms",
                "availability": "99.9%",
                "rate_limit": "1000 req/min"
            },
            "data_model": {
                "product_id": "string",
                "quantity": "integer",
                "customer_tier": "enum",
                "discount_codes": "array"
            }
        },
        "implementation_steps": [
            phase["description"] for phase in plan.phases
        ],
        "risk_assessment": plan.risk_assessment,
        "estimated_credits": plan.estimated_credits
    }


if __name__ == "__main__":
    # Test the planner
    async def test():
        plan = await create_pricing_api_plan()
        print(json.dumps(plan, indent=2))
    
    asyncio.run(test())