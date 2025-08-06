#!/usr/bin/env python3
"""Tests for the Planner Agent."""
import asyncio
import json
import pytest
from pathlib import Path
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.planner_agent import (
    PlannerAgent, 
    TaskPlan, 
    TaskComplexity,
    create_pricing_api_plan
)


class TestPlannerAgent:
    """Test suite for Planner Agent."""
    
    @pytest.mark.asyncio
    async def test_create_simple_plan(self):
        """Test creating a simple plan."""
        planner = PlannerAgent()
        
        task = {
            "id": "TEST-001",
            "feature": "Simple data export",
            "agents": ["planner"]
        }
        
        plan = await planner.create_plan(task)
        
        assert plan.task_id == "TEST-001"
        assert plan.complexity == TaskComplexity.SIMPLE
        assert "planner" in plan.agents_required
        assert len(plan.phases) >= 2  # At least analysis and review
        assert plan.estimated_credits > 0
    
    @pytest.mark.asyncio
    async def test_create_complex_plan(self):
        """Test creating a complex plan with multiple agents."""
        planner = PlannerAgent()
        
        task = {
            "id": "TEST-002",
            "feature": "Real-time data processing pipeline",
            "agents": ["planner", "codegen", "stress-tester", "sla-verifier"]
        }
        
        plan = await planner.create_plan(task)
        
        assert plan.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL]
        assert len(plan.agents_required) >= 4
        assert len(plan.phases) >= 4
        assert plan.estimated_credits >= 400
        assert plan.risk_assessment["technical_risk"] in ["MEDIUM", "HIGH"]
    
    @pytest.mark.asyncio
    async def test_critical_task_detection(self):
        """Test that SLA/security tasks are marked critical."""
        planner = PlannerAgent()
        
        task = {
            "id": "TEST-003",
            "feature": "Authentication service with SLA",
            "agents": ["planner", "codegen"]
        }
        
        plan = await planner.create_plan(task)
        
        assert plan.complexity == TaskComplexity.CRITICAL
        assert "sla-verifier" in plan.agents_required  # Auto-added for critical
        assert any("SLA" in phase["name"] for phase in plan.phases)
        assert plan.risk_assessment["overall_risk"] in ["MEDIUM", "HIGH"]
    
    @pytest.mark.asyncio
    async def test_validation_steps(self):
        """Test that appropriate validation steps are created."""
        planner = PlannerAgent()
        
        task = {
            "id": "TEST-004",
            "feature": "REST API with testing",
            "agents": ["planner", "codegen", "stress-tester"]
        }
        
        plan = await planner.create_plan(task)
        
        assert len(plan.validation_steps) >= 3
        assert any("API" in step for step in plan.validation_steps)
        assert any("test" in step.lower() for step in plan.validation_steps)
    
    @pytest.mark.asyncio
    async def test_credit_estimation(self):
        """Test credit estimation accuracy."""
        planner = PlannerAgent()
        
        # Simple task
        simple_task = {
            "id": "SIMPLE",
            "feature": "Basic report",
            "agents": ["planner"]
        }
        simple_plan = await planner.create_plan(simple_task)
        
        # Complex task
        complex_task = {
            "id": "COMPLEX",
            "feature": "Real-time analytics dashboard",
            "agents": ["planner", "codegen", "stress-tester", "sla-verifier"]
        }
        complex_plan = await planner.create_plan(complex_task)
        
        # Complex should cost more
        assert complex_plan.estimated_credits > simple_plan.estimated_credits
        assert simple_plan.estimated_credits <= 200
        assert complex_plan.estimated_credits >= 400
    
    @pytest.mark.asyncio
    async def test_pilot_001_compatibility(self):
        """Test compatibility with PILOT-001 test."""
        plan = await create_pricing_api_plan()
        
        # Check expected structure
        assert "api_design" in plan
        assert "implementation_steps" in plan
        assert "risk_assessment" in plan
        assert "estimated_credits" in plan
        
        # Check API design
        api = plan["api_design"]
        assert "endpoints" in api
        assert len(api["endpoints"]) >= 3
        assert "sla" in api
        assert api["sla"]["response_time_p99"] == "100ms"
        
        # Check credit estimation
        assert plan["estimated_credits"] >= 400
        assert plan["estimated_credits"] <= 500
    
    @pytest.mark.asyncio  
    async def test_metrics_tracking(self):
        """Test that metrics are properly tracked."""
        planner = PlannerAgent()
        
        # Create multiple plans
        for i in range(3):
            task = {
                "id": f"METRIC-{i}",
                "feature": f"Feature {i}",
                "agents": ["planner", "codegen"]
            }
            await planner.create_plan(task)
        
        metrics = planner.get_metrics()
        
        assert metrics["agent"] == "planner"
        assert metrics["plans_created"] == 3
        assert metrics["total_credits_estimated"] > 0
        assert metrics["avg_credits_per_plan"] > 0


def test_task_complexity_enum():
    """Test TaskComplexity enum values."""
    assert TaskComplexity.SIMPLE.value == "simple"
    assert TaskComplexity.COMPLEX.value == "complex"
    assert TaskComplexity.CRITICAL.value == "critical"


def test_task_plan_dataclass():
    """Test TaskPlan dataclass."""
    plan = TaskPlan(
        task_id="TEST",
        feature="Test feature",
        complexity=TaskComplexity.SIMPLE,
        phases=[],
        agents_required=["planner"],
        estimated_credits=100,
        validation_steps=["Test step"],
        risk_assessment={"overall_risk": "LOW"}
    )
    
    assert plan.task_id == "TEST"
    assert plan.created_at  # Auto-populated
    assert "T" in plan.created_at  # ISO format


if __name__ == "__main__":
    # Run basic tests
    print("Testing Planner Agent...")
    
    async def run_basic_test():
        planner = PlannerAgent()
        
        # Test 1: Simple task
        print("\n1. Testing simple task...")
        simple_task = {
            "id": "MANUAL-001",
            "feature": "Basic report generation",
            "agents": ["planner"]
        }
        simple_plan = await planner.create_plan(simple_task)
        print(f"   ✅ Created plan with {len(simple_plan.phases)} phases")
        print(f"   Credits: {simple_plan.estimated_credits}")
        
        # Test 2: Complex task
        print("\n2. Testing complex task...")
        complex_task = {
            "id": "MANUAL-002",
            "feature": "Real-time API with SLA",
            "agents": ["planner", "codegen", "stress-tester", "sla-verifier"]
        }
        complex_plan = await planner.create_plan(complex_task)
        print(f"   ✅ Created plan with {len(complex_plan.phases)} phases")
        print(f"   Credits: {complex_plan.estimated_credits}")
        print(f"   Risk: {complex_plan.risk_assessment['overall_risk']}")
        
        # Test 3: PILOT-001 compatibility
        print("\n3. Testing PILOT-001 compatibility...")
        pilot_plan = await create_pricing_api_plan()
        print(f"   ✅ Created pricing API plan")
        print(f"   Endpoints: {len(pilot_plan['api_design']['endpoints'])}")
        print(f"   Credits: {pilot_plan['estimated_credits']}")
        
        print("\n✅ All manual tests passed!")
    
    asyncio.run(run_basic_test())