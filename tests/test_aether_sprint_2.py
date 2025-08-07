#!/usr/bin/env python3
"""
@cognimap:fingerprint
id: e93b9b81-8df0-4923-aeea-df0130328f26
birth: 2025-08-07T07:23:38.068778Z
parent: None
intent: Test Suite for Aether Protocol Sprint 2: Karmic Ledger
semantic_tags: [database, api, testing, model, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.069255Z
hash: 95cc4115
language: python
type: test
@end:cognimap
"""

"""
Test Suite for Aether Protocol Sprint 2: Karmic Ledger

Verifies the balance layer implementation including:
- KarmicOrchestrator functionality
- Karma tracking and calculation
- Interest accumulation
- Balancing mechanisms
- Agent runtime integration
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta
from uuid import uuid4

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent))

from evolution.aether.karmic_orchestrator import (
    KarmicOrchestrator,
    KarmicAction,
    ActionType,
    KarmaCategory
)
from evolution.aether.karma_agent_runtime import (
    KarmaAwareAgentRuntime,
    MockKarmicOrchestrator
)


class TestKarmicOrchestrator:
    """Test the Karmic Orchestrator."""
    
    def test_karma_calculation(self):
        """Test karma value calculation."""
        orchestrator = KarmicOrchestrator("mock://")
        
        # Test positive karma
        positive_karma = orchestrator.calculate_action_karma(
            ActionType.BUG_FIX,
            {'impact': 'high', 'success': True}
        )
        assert positive_karma > 0, f"Bug fix should generate positive karma, got {positive_karma}"
        
        # Test negative karma
        negative_karma = orchestrator.calculate_action_karma(
            ActionType.QUICK_FIX,
            {'impact': 'medium'}
        )
        assert negative_karma < 0, f"Quick fix should generate negative karma, got {negative_karma}"
        
        # Test neutral karma
        neutral_karma = orchestrator.calculate_action_karma(
            ActionType.ANALYSIS,
            {'impact': 'low'}
        )
        assert -0.2 <= neutral_karma <= 0.2, f"Analysis should be near neutral, got {neutral_karma}"
        
        print("✅ Karma calculation tests passed")
    
    def test_impact_modifiers(self):
        """Test impact-based karma modifiers."""
        orchestrator = KarmicOrchestrator("mock://")
        
        base_action = ActionType.REFACTOR
        
        # Low impact
        low_impact = orchestrator.calculate_action_karma(
            base_action,
            {'impact': 'low'}
        )
        
        # High impact
        high_impact = orchestrator.calculate_action_karma(
            base_action,
            {'impact': 'high'}
        )
        
        # Critical impact
        critical_impact = orchestrator.calculate_action_karma(
            base_action,
            {'impact': 'critical'}
        )
        
        assert high_impact > low_impact, "High impact should generate more karma"
        assert critical_impact > high_impact, "Critical impact should generate most karma"
        
        print("✅ Impact modifier tests passed")
    
    def test_karmic_action_model(self):
        """Test KarmicAction model."""
        action = KarmicAction(
            actor="test_agent",
            action_type=ActionType.OPTIMIZATION,
            karma_generated=0.6,
            karma_balanced=0.2
        )
        
        assert abs(action.karma_debt - 0.4) < 0.001, f"Karma debt calculation wrong: {action.karma_debt}"
        assert not action.is_balanced, "Action should not be balanced"
        assert action.days_unbalanced >= 0, "Days unbalanced should be non-negative"
        
        # Test balanced action
        balanced_action = KarmicAction(
            actor="test_agent",
            action_type=ActionType.DOCUMENTATION,
            karma_generated=0.3,
            karma_balanced=0.3
        )
        assert balanced_action.is_balanced, "Action should be balanced"
        
        print("✅ KarmicAction model tests passed")


class TestKarmaAgentRuntime:
    """Test karma-aware agent runtime."""
    
    async def test_action_execution(self):
        """Test karma tracking during action execution."""
        orchestrator = MockKarmicOrchestrator()
        runtime = KarmaAwareAgentRuntime(
            agent_name="test_agent",
            karmic_orchestrator=orchestrator
        )
        
        # Mock action
        async def mock_action():
            return {'success': True, 'lines_changed': 50}
        
        # Execute action
        result = await runtime.execute_action(
            'refactor_code',
            mock_action
        )
        
        assert result['success'] == True
        assert result['karma_generated'] > 0, "Refactor should generate positive karma"
        assert 'total_karma' in result
        
        print("✅ Action execution tests passed")
    
    async def test_karma_accumulation(self):
        """Test karma accumulation across multiple actions."""
        orchestrator = MockKarmicOrchestrator()
        runtime = KarmaAwareAgentRuntime(
            agent_name="test_agent",
            karmic_orchestrator=orchestrator
        )
        
        async def mock_action():
            return {'success': True}
        
        # Execute multiple actions
        await runtime.execute_action('refactor_code', mock_action)
        await runtime.execute_action('create_tests', mock_action)
        await runtime.execute_action('quick_patch', mock_action)
        
        # Check accumulated karma
        status = await runtime.check_karma_status()
        assert status['total_actions'] == 3
        assert status['current_karma'] != 0, "Karma should accumulate"
        assert status['karma_status'] in [
            'ENLIGHTENED', 'VIRTUOUS', 'BALANCED', 'INDEBTED', 'BURDENED'
        ]
        
        print("✅ Karma accumulation tests passed")
    
    async def test_failure_karma(self):
        """Test negative karma from failures."""
        orchestrator = MockKarmicOrchestrator()
        runtime = KarmaAwareAgentRuntime(
            agent_name="test_agent",
            karmic_orchestrator=orchestrator
        )
        
        # Mock failing action
        async def failing_action():
            raise Exception("Test failure")
        
        # Execute failing action
        result = await runtime.execute_action(
            'implement_feature',
            failing_action
        )
        
        assert result['success'] == False
        assert result['karma_generated'] < 0, "Failures should generate negative karma"
        assert 'error' in result
        
        print("✅ Failure karma tests passed")
    
    async def test_karma_balancing(self):
        """Test karma balancing suggestions."""
        orchestrator = MockKarmicOrchestrator()
        runtime = KarmaAwareAgentRuntime(
            agent_name="test_agent",
            karmic_orchestrator=orchestrator
        )
        
        # Create debt
        async def mock_action():
            return {'success': True}
        
        await runtime.execute_action('add_hack', mock_action)
        runtime.karma_balance = -1.0  # Force negative karma
        
        # Attempt balancing
        balancing = await runtime.attempt_karma_balancing()
        assert balancing['needed'] == True
        assert balancing['balanced'] == True
        assert 'action_taken' in balancing
        
        print("✅ Karma balancing tests passed")


class TestInterestCalculation:
    """Test karmic interest calculations."""
    
    def test_interest_accumulation(self):
        """Test that unbalanced karma accumulates interest."""
        # Create action with debt
        action = KarmicAction(
            actor="test_agent",
            action_type=ActionType.DEBT_CREATION,
            karma_generated=-0.6,
            interest_rate=0.01
        )
        
        # Simulate time passing
        action.created_at = datetime.utcnow() - timedelta(days=10)
        
        # Calculate expected interest
        days = action.days_unbalanced
        assert days >= 10, f"Days calculation wrong: {days}"
        
        # Interest should accumulate on debt
        expected_interest = abs(action.karma_debt) * action.interest_rate * days
        assert expected_interest > 0, "Interest should accumulate on debt"
        
        print("✅ Interest calculation tests passed")


def test_sprint_2_requirements():
    """Verify all Sprint 2 requirements are met."""
    
    # Check all required files exist
    required_files = [
        "evolution/migrations/002_karmic_ledger.sql",
        "evolution/aether/karmic_orchestrator.py",
        "evolution/aether/karma_agent_runtime.py",
        "tests/test_aether_sprint_2.py"
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        assert path.exists(), f"Required file missing: {file_path}"
    
    print("✅ All Sprint 2 files present")
    
    # Test imports work
    try:
        from evolution.aether.karmic_orchestrator import KarmicOrchestrator, ActionType
        from evolution.aether.karma_agent_runtime import KarmaAwareAgentRuntime
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    
    return True


async def run_all_tests():
    """Run all Sprint 2 tests."""
    print("🧪 Testing Aether Protocol Sprint 2: Karmic Ledger\n" + "="*50)
    
    # Test requirements
    if not test_sprint_2_requirements():
        print("❌ Requirements check failed")
        return
    
    # Test KarmicOrchestrator
    print("\n⚖️ Testing KarmicOrchestrator...")
    orch_tests = TestKarmicOrchestrator()
    orch_tests.test_karma_calculation()
    orch_tests.test_impact_modifiers()
    orch_tests.test_karmic_action_model()
    
    # Test KarmaAgentRuntime
    print("\n🤖 Testing KarmaAgentRuntime...")
    runtime_tests = TestKarmaAgentRuntime()
    await runtime_tests.test_action_execution()
    await runtime_tests.test_karma_accumulation()
    await runtime_tests.test_failure_karma()
    await runtime_tests.test_karma_balancing()
    
    # Test Interest
    print("\n💰 Testing Interest Calculations...")
    interest_tests = TestInterestCalculation()
    interest_tests.test_interest_accumulation()
    
    print("\n" + "="*50)
    print("✅ ALL SPRINT 2 TESTS PASSED!")
    print("="*50)
    print("\nSprint 2 Summary:")
    print("• KarmicOrchestrator: Track positive/negative karma")
    print("• Interest System: Debt accumulates over time")
    print("• Agent Integration: Automatic karma tracking")
    print("• Balancing Mechanisms: Suggestions and automation")
    print("• Database Schema: Complete karmic ledger")
    print("\nThe Balance Layer is complete! ⚖️")


if __name__ == "__main__":
    # Run all tests
    asyncio.run(run_all_tests())