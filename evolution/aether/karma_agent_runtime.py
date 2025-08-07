#!/usr/bin/env python3
"""
@cognimap:fingerprint
id: 3d5bff7d-7987-453e-ad92-d34e1b282b20
birth: 2025-08-07T07:23:38.091570Z
parent: None
intent: Karma-Aware Agent Runtime
semantic_tags: [database, api, testing, ui, configuration, security]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.092076Z
hash: fa7f2676
language: python
type: agent
@end:cognimap
"""

"""
Karma-Aware Agent Runtime

Extends agent runtime to automatically track karmic consequences of all actions.
Part of Sprint 2: Foundation of Balance.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID
import sys
from pathlib import Path

# Add parent paths
sys.path.append(str(Path(__file__).parent.parent.parent))

from evolution.aether.karmic_orchestrator import (
    KarmicOrchestrator,
    ActionType,
    KarmicAction
)
try:
    from evolution.aether.intent_substrate import IntentSubstrate
except ImportError:
    IntentSubstrate = None  # For testing without database

logger = logging.getLogger(__name__)


class KarmaAwareAgentRuntime:
    """
    Agent runtime that tracks karmic consequences of all actions.
    
    Every agent action is evaluated for its karmic impact and recorded
    in the ledger. Agents accumulate karma (positive or negative) based
    on their actions.
    """
    
    def __init__(
        self,
        agent_name: str,
        karmic_orchestrator: KarmicOrchestrator,
        intent_substrate: Optional[IntentSubstrate] = None
    ):
        self.agent_name = agent_name
        self.karmic_orch = karmic_orchestrator
        self.intent_substrate = intent_substrate
        
        # Track current intent
        self.current_intent_id: Optional[UUID] = None
        
        # Action history
        self.action_history: List[KarmicAction] = []
        self.karma_balance = 0.0
        
        # Action mapping for agents
        self.agent_action_mapping = {
            # Planner actions
            'create_plan': ActionType.PLANNING,
            'optimize_plan': ActionType.OPTIMIZATION,
            
            # Codegen actions
            'generate_code': ActionType.FEATURE_COMPLETE,
            'quick_patch': ActionType.QUICK_FIX,
            'create_tests': ActionType.TEST_CREATION,
            
            # Tester actions
            'run_tests': ActionType.REVIEW,
            'skip_tests': ActionType.TEST_SKIP,
            'fix_tests': ActionType.BUG_FIX,
            
            # Implementor actions
            'implement_feature': ActionType.FEATURE_COMPLETE,
            'refactor_code': ActionType.REFACTOR,
            'add_hack': ActionType.HACK,
            
            # Architect actions
            'design_system': ActionType.PLANNING,
            'document_architecture': ActionType.DOCUMENTATION,
            'breaking_redesign': ActionType.BREAKING_CHANGE,
            
            # Treasurer actions
            'optimize_costs': ActionType.OPTIMIZATION,
            'analyze_spending': ActionType.ANALYSIS,
            
            # Security actions
            'fix_vulnerability': ActionType.SECURITY_FIX,
            'introduce_vulnerability': ActionType.SECURITY_VULNERABILITY
        }
    
    def set_intent(self, intent_id: UUID):
        """Set the current intent context."""
        self.current_intent_id = intent_id
        logger.debug(f"{self.agent_name} operating under intent {intent_id}")
    
    async def execute_action(
        self,
        action_name: str,
        action_func: callable,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an action and track its karmic consequences.
        """
        start_time = datetime.utcnow()
        result = {'success': False, 'karma_generated': 0.0}
        
        try:
            # Execute the actual action
            action_result = await action_func(**kwargs)
            
            # Determine success
            success = action_result.get('success', True) if isinstance(action_result, dict) else True
            
            # Calculate impact
            impact = self._calculate_impact(action_name, action_result)
            
            # Map to karma action type
            karma_action_type = self.agent_action_mapping.get(
                action_name,
                ActionType.ANALYSIS  # Default neutral
            )
            
            # Record karma
            details = {
                'success': success,
                'impact': impact,
                'duration': (datetime.utcnow() - start_time).total_seconds(),
                'agent': self.agent_name
            }
            
            if isinstance(action_result, dict):
                details.update(action_result)
            
            karma_action = await self.karmic_orch.record_action(
                actor=self.agent_name,
                action_type=karma_action_type,
                intent_id=self.current_intent_id,
                details=details
            )
            
            # Update local tracking
            self.action_history.append(karma_action)
            self.karma_balance += karma_action.karma_generated
            
            # Prepare result
            result = {
                'success': success,
                'karma_generated': karma_action.karma_generated,
                'total_karma': self.karma_balance,
                'action_result': action_result
            }
            
            # Log karma impact
            karma_symbol = "✅" if karma_action.karma_generated > 0 else "⚠️" if karma_action.karma_generated < 0 else "ℹ️"
            logger.info(
                f"{karma_symbol} {self.agent_name} executed {action_name}: "
                f"Karma {karma_action.karma_generated:+.2f} (Total: {self.karma_balance:+.2f})"
            )
            
        except Exception as e:
            # Failures generate negative karma
            logger.error(f"{self.agent_name} action {action_name} failed: {e}")
            
            # Record failure karma
            karma_action = await self.karmic_orch.record_action(
                actor=self.agent_name,
                action_type=ActionType.DEBT_CREATION,
                intent_id=self.current_intent_id,
                details={
                    'error': str(e),
                    'action': action_name,
                    'success': False
                }
            )
            
            self.karma_balance += karma_action.karma_generated
            
            result = {
                'success': False,
                'error': str(e),
                'karma_generated': karma_action.karma_generated,
                'total_karma': self.karma_balance
            }
        
        return result
    
    def _calculate_impact(self, action_name: str, action_result: Any) -> str:
        """
        Calculate the impact level of an action.
        """
        # Critical actions
        if 'security' in action_name.lower() or 'breaking' in action_name.lower():
            return 'critical'
        
        # High impact actions
        if any(word in action_name.lower() for word in ['implement', 'fix', 'optimize']):
            return 'high'
        
        # Low impact actions
        if any(word in action_name.lower() for word in ['analyze', 'plan', 'review']):
            return 'low'
        
        # Check result for impact hints
        if isinstance(action_result, dict):
            if action_result.get('lines_changed', 0) > 100:
                return 'high'
            if action_result.get('tests_added', 0) > 10:
                return 'high'
            if action_result.get('errors_fixed', 0) > 5:
                return 'high'
        
        return 'medium'
    
    async def check_karma_status(self) -> Dict[str, Any]:
        """
        Check the agent's current karma status.
        """
        # Get suggestions for balancing
        suggestions = await self.karmic_orch.suggest_balancing_actions(
            self.agent_name,
            limit=3
        )
        
        # Calculate interest
        interest = await self.karmic_orch.calculate_interest(self.agent_name)
        
        status = {
            'agent': self.agent_name,
            'current_karma': self.karma_balance,
            'total_actions': len(self.action_history),
            'karma_status': self._get_karma_status(),
            'accumulated_interest': interest['total_interest'],
            'balancing_suggestions': suggestions
        }
        
        return status
    
    def _get_karma_status(self) -> str:
        """
        Determine karma status based on balance.
        """
        if self.karma_balance >= 2.0:
            return "ENLIGHTENED"  # Very positive karma
        elif self.karma_balance >= 1.0:
            return "VIRTUOUS"     # Positive karma
        elif self.karma_balance >= 0:
            return "BALANCED"     # Neutral
        elif self.karma_balance >= -1.0:
            return "INDEBTED"     # Negative karma
        else:
            return "BURDENED"     # Heavy karmic debt
    
    async def attempt_karma_balancing(self) -> Dict[str, Any]:
        """
        Attempt to balance negative karma with positive actions.
        """
        if self.karma_balance >= 0:
            return {
                'needed': False,
                'message': 'No karmic debt to balance'
            }
        
        # Get balancing suggestions
        suggestions = await self.karmic_orch.suggest_balancing_actions(
            self.agent_name,
            limit=1
        )
        
        if not suggestions or 'action_type' not in suggestions[0]:
            return {
                'needed': True,
                'balanced': False,
                'message': 'No balancing actions available'
            }
        
        # Execute balancing action
        suggestion = suggestions[0]
        logger.info(
            f"🔄 {self.agent_name} attempting karmic balancing: {suggestion['action_type']}"
        )
        
        # Record the balancing action
        balancing_action = await self.karmic_orch.record_action(
            actor=self.agent_name,
            action_type=suggestion['action_type'],
            intent_id=self.current_intent_id,
            details={
                'purpose': 'karmic_balancing',
                'automated': True
            }
        )
        
        self.karma_balance += balancing_action.karma_generated
        
        return {
            'needed': True,
            'balanced': True,
            'action_taken': suggestion['action_type'],
            'karma_generated': balancing_action.karma_generated,
            'new_balance': self.karma_balance
        }


# Mock implementations for testing
class MockKarmicOrchestrator:
    """Mock orchestrator for testing without database."""
    
    def __init__(self):
        self.actions = []
    
    async def record_action(self, actor, action_type, intent_id=None, details=None):
        from evolution.aether.karmic_orchestrator import KarmicAction
        
        # Simple karma calculation
        karma_map = {
            'refactor': 0.5,
            'test_creation': 0.4,
            'documentation': 0.3,
            'quick_fix': -0.3,
            'hack': -0.5,
            'debt_creation': -0.6
        }
        
        karma = karma_map.get(action_type, 0.1)
        
        action = KarmicAction(
            actor=actor,
            action_type=action_type,
            intent_id=intent_id,
            karma_generated=karma,
            action_details=details or {}
        )
        
        self.actions.append(action)
        return action
    
    async def suggest_balancing_actions(self, actor, limit=3):
        return [
            {
                'action_type': 'refactor',
                'expected_karma': 0.5,
                'description': 'Refactor code for clarity'
            }
        ]
    
    async def calculate_interest(self, actor):
        return {'total_interest': 0.05}


# Example usage and testing
async def demo_karma_agent_runtime():
    """
    Demonstrate karma-aware agent runtime.
    """
    # Use mock orchestrator for demo
    orchestrator = MockKarmicOrchestrator()
    
    # Create runtime for a developer agent
    runtime = KarmaAwareAgentRuntime(
        agent_name="developer_agent",
        karmic_orchestrator=orchestrator
    )
    
    print("\n🤖 Karma-Aware Agent Runtime Demo\n" + "="*50)
    
    # Simulate agent actions
    async def mock_refactor():
        await asyncio.sleep(0.1)
        return {'success': True, 'lines_changed': 150}
    
    async def mock_quick_fix():
        await asyncio.sleep(0.05)
        return {'success': True, 'lines_changed': 10}
    
    async def mock_test_creation():
        await asyncio.sleep(0.2)
        return {'success': True, 'tests_added': 15}
    
    # Execute actions
    print("\n1. Executing agent actions...")
    
    result1 = await runtime.execute_action('refactor_code', mock_refactor)
    print(f"  Refactor: Karma {result1['karma_generated']:+.2f}")
    
    result2 = await runtime.execute_action('quick_patch', mock_quick_fix)
    print(f"  Quick fix: Karma {result2['karma_generated']:+.2f}")
    
    result3 = await runtime.execute_action('create_tests', mock_test_creation)
    print(f"  Create tests: Karma {result3['karma_generated']:+.2f}")
    
    # Check karma status
    print("\n2. Checking karma status...")
    status = await runtime.check_karma_status()
    print(f"  Agent: {status['agent']}")
    print(f"  Total Karma: {status['current_karma']:+.2f}")
    print(f"  Status: {status['karma_status']}")
    print(f"  Actions: {status['total_actions']}")
    
    # Attempt balancing if needed
    print("\n3. Attempting karma balancing...")
    balancing = await runtime.attempt_karma_balancing()
    if balancing['needed']:
        if balancing.get('balanced'):
            print(f"  Balanced with: {balancing['action_taken']}")
            print(f"  New balance: {balancing['new_balance']:+.2f}")
        else:
            print(f"  {balancing['message']}")
    else:
        print(f"  {balancing['message']}")
    
    print("\n" + "="*50)
    print("✅ Karma-aware agent runtime ready!")


if __name__ == "__main__":
    print("\n⚖️ Karma-Aware Agent Runtime\n" + "="*50)
    print("This module extends agents with automatic karma tracking.")
    print("\nKey features:")
    print("- Automatic karma calculation for all actions")
    print("- Impact assessment based on action type")
    print("- Karma balance tracking per agent")
    print("- Automatic balancing suggestions")
    print("="*50)
    
    # Run demo
    asyncio.run(demo_karma_agent_runtime())