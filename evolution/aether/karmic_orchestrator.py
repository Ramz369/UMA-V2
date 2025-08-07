#!/usr/bin/env python3
"""
Karmic Orchestrator - The Balance Layer of the Aether Protocol

This module implements Sprint 2: Foundation of Balance, managing karmic
debt and credit in the system. Every action creates karma that must
eventually be balanced.

Karma represents the long-term consequences of actions:
- Positive karma: Constructive actions that improve the system
- Negative karma: Destructive actions that create debt
- Interest: Unresolved karma accumulates interest over time
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID, uuid4
try:
    import asyncpg
except ImportError:
    asyncpg = None  # For testing without database
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class KarmaCategory(str, Enum):
    """Categories of karmic actions."""
    CONSTRUCTIVE = "constructive"  # Builds up the system
    DESTRUCTIVE = "destructive"    # Tears down or creates debt
    NEUTRAL = "neutral"           # Neither good nor bad


class ActionType(str, Enum):
    """Standard action types with karmic values."""
    # Constructive actions
    REFACTOR = "refactor"
    TEST_CREATION = "test_creation"
    DOCUMENTATION = "documentation"
    OPTIMIZATION = "optimization"
    BUG_FIX = "bug_fix"
    FEATURE_COMPLETE = "feature_complete"
    SECURITY_FIX = "security_fix"
    
    # Destructive actions
    QUICK_FIX = "quick_fix"
    HACK = "hack"
    TEST_SKIP = "test_skip"
    DEBT_CREATION = "debt_creation"
    BREAKING_CHANGE = "breaking_change"
    SECURITY_VULNERABILITY = "security_vulnerability"
    
    # Neutral actions
    ANALYSIS = "analysis"
    PLANNING = "planning"
    REVIEW = "review"


class KarmicAction(BaseModel):
    """Model representing a karmic action."""
    
    karma_id: UUID = Field(default_factory=uuid4)
    actor: str
    action_type: str
    intent_id: Optional[UUID] = None
    
    # Karmic values
    karma_generated: float
    karma_balanced: float = 0.0
    
    # Interest tracking
    interest_rate: float = 0.01  # 1% daily
    accumulated_interest: float = 0.0
    
    # Cycle tracking
    cycle_number: int = 1
    cycle_completion: float = 0.0
    
    # Metadata
    action_details: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    balanced_at: Optional[datetime] = None
    
    @property
    def karma_debt(self) -> float:
        """Calculate current karma debt."""
        return self.karma_generated - self.karma_balanced
    
    @property
    def is_balanced(self) -> bool:
        """Check if karma is balanced."""
        return abs(self.karma_debt) < 0.01  # Small threshold for floating point
    
    @property
    def days_unbalanced(self) -> float:
        """Calculate days since karma was generated."""
        if self.balanced_at:
            return 0.0
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds() / 86400


class KarmicOrchestrator:
    """
    Manages karmic balance in the system.
    
    Key responsibilities:
    - Track karma generation from actions
    - Calculate and apply interest on unbalanced karma
    - Suggest balancing actions
    - Monitor system-wide karmic health
    """
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool: Optional[asyncpg.Pool] = None
        
        # Karma values for standard actions
        self.karma_values = {
            # Constructive
            ActionType.REFACTOR: 0.5,
            ActionType.TEST_CREATION: 0.4,
            ActionType.DOCUMENTATION: 0.3,
            ActionType.OPTIMIZATION: 0.6,
            ActionType.BUG_FIX: 0.7,
            ActionType.FEATURE_COMPLETE: 0.8,
            ActionType.SECURITY_FIX: 0.9,
            
            # Destructive
            ActionType.QUICK_FIX: -0.3,
            ActionType.HACK: -0.5,
            ActionType.TEST_SKIP: -0.4,
            ActionType.DEBT_CREATION: -0.6,
            ActionType.BREAKING_CHANGE: -0.7,
            ActionType.SECURITY_VULNERABILITY: -0.9,
            
            # Neutral
            ActionType.ANALYSIS: 0.1,
            ActionType.PLANNING: 0.1,
            ActionType.REVIEW: 0.2
        }
    
    async def initialize(self):
        """Initialize database connection and ensure schema exists."""
        self.pool = await asyncpg.create_pool(self.db_url)
        
        # Run migration if needed
        async with self.pool.acquire() as conn:
            # Check if table exists
            exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'evolution' 
                    AND table_name = 'karmic_ledger'
                );
            """)
            
            if not exists:
                # Run the migration
                with open('evolution/migrations/002_karmic_ledger.sql', 'r') as f:
                    migration_sql = f.read()
                await conn.execute(migration_sql)
                logger.info("✅ Karmic ledger initialized")
    
    async def record_action(
        self,
        actor: str,
        action_type: str,
        intent_id: Optional[UUID] = None,
        details: Optional[Dict] = None
    ) -> KarmicAction:
        """
        Record a karmic action in the ledger.
        """
        # Calculate karma value
        karma_value = self.calculate_action_karma(action_type, details)
        
        # Create action record
        action = KarmicAction(
            actor=actor,
            action_type=action_type,
            intent_id=intent_id,
            karma_generated=karma_value,
            action_details=details or {}
        )
        
        # Store in database
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO evolution.karmic_ledger (
                    karma_id, actor, action_type, intent_id,
                    karma_generated, karma_balanced,
                    interest_rate, accumulated_interest,
                    cycle_number, cycle_completion,
                    action_details, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """,
                action.karma_id,
                action.actor,
                action.action_type,
                action.intent_id,
                action.karma_generated,
                action.karma_balanced,
                action.interest_rate,
                action.accumulated_interest,
                action.cycle_number,
                action.cycle_completion,
                json.dumps(action.action_details),
                action.created_at
            )
        
        # Log the action
        karma_type = "positive" if karma_value > 0 else "negative" if karma_value < 0 else "neutral"
        logger.info(
            f"⚖️ Karma recorded: {actor} performed {action_type} "
            f"({karma_type}: {karma_value:+.2f})"
        )
        
        return action
    
    def calculate_action_karma(
        self,
        action_type: str,
        details: Optional[Dict] = None
    ) -> float:
        """
        Calculate karma value for an action.
        """
        # Base karma from action type
        base_karma = self.karma_values.get(action_type, 0.0)
        
        # Adjust based on details
        if details:
            # Impact modifier
            impact = details.get('impact', 'medium')
            impact_modifiers = {'low': 0.5, 'medium': 1.0, 'high': 1.5, 'critical': 2.0}
            base_karma *= impact_modifiers.get(impact, 1.0)
            
            # Success modifier
            if 'success' in details:
                if not details['success'] and base_karma > 0:
                    base_karma *= -0.5  # Failed positive action creates debt
            
            # Complexity modifier
            complexity = details.get('complexity', 1.0)
            base_karma *= min(2.0, max(0.5, complexity))
        
        return round(base_karma, 3)
    
    async def calculate_interest(
        self,
        actor: Optional[str] = None,
        apply_interest: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate accumulated interest on unbalanced karma.
        """
        async with self.pool.acquire() as conn:
            # Get unbalanced karma
            query = """
                SELECT karma_id, actor, karma_debt, interest_rate, 
                       created_at, last_interest_update
                FROM evolution.karmic_ledger
                WHERE balanced_at IS NULL AND karma_debt != 0
            """
            
            if actor:
                query += " AND actor = $1"
                rows = await conn.fetch(query, actor)
            else:
                rows = await conn.fetch(query)
            
            total_interest = 0.0
            interest_details = []
            
            for row in rows:
                # Calculate days since last update
                last_update = row['last_interest_update'] or row['created_at']
                days_passed = (datetime.utcnow() - last_update).total_seconds() / 86400
                
                # Only negative karma (debt) accumulates interest
                if row['karma_debt'] > 0:
                    interest = row['karma_debt'] * row['interest_rate'] * days_passed
                    total_interest += interest
                    
                    interest_details.append({
                        'karma_id': row['karma_id'],
                        'actor': row['actor'],
                        'debt': row['karma_debt'],
                        'days': days_passed,
                        'interest': interest
                    })
                    
                    # Apply interest if requested
                    if apply_interest and interest > 0:
                        await conn.execute("""
                            UPDATE evolution.karmic_ledger
                            SET accumulated_interest = accumulated_interest + $1,
                                karma_generated = karma_generated + $1,
                                last_interest_update = NOW()
                            WHERE karma_id = $2
                        """, interest, row['karma_id'])
            
            return {
                'total_interest': total_interest,
                'entries': len(interest_details),
                'details': interest_details[:10]  # Top 10
            }
    
    async def suggest_balancing_actions(
        self,
        actor: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Suggest actions to balance karma.
        """
        async with self.pool.acquire() as conn:
            # Get actor's current karma
            karma_status = await conn.fetchrow("""
                SELECT 
                    SUM(karma_debt) as total_debt,
                    SUM(CASE WHEN karma_generated > 0 THEN karma_generated ELSE 0 END) as positive_karma,
                    SUM(CASE WHEN karma_generated < 0 THEN ABS(karma_generated) ELSE 0 END) as negative_karma
                FROM evolution.karmic_ledger
                WHERE actor = $1 AND balanced_at IS NULL
            """, actor)
            
            if not karma_status or karma_status['total_debt'] is None:
                return []
            
            total_debt = karma_status['total_debt']
            
            # If no debt, no balancing needed
            if total_debt <= 0:
                return [{
                    'message': 'No karmic debt to balance!',
                    'status': 'balanced'
                }]
            
            # Get suggested actions from database
            suggestions = await conn.fetch("""
                SELECT * FROM evolution.suggest_balancing_actions($1, $2)
            """, actor, limit)
            
            # Calculate how many of each action needed
            result = []
            remaining_debt = total_debt
            
            for suggestion in suggestions:
                if remaining_debt <= 0:
                    break
                
                times_needed = max(1, int(remaining_debt / suggestion['expected_karma']))
                
                result.append({
                    'action_type': suggestion['action_type'],
                    'expected_karma': suggestion['expected_karma'],
                    'description': suggestion['description'],
                    'times_needed': times_needed,
                    'total_karma': suggestion['expected_karma'] * times_needed
                })
                
                remaining_debt -= suggestion['expected_karma'] * times_needed
            
            return result
    
    async def balance_karma(
        self,
        debt_karma_id: UUID,
        credit_karma_id: UUID
    ) -> bool:
        """
        Balance karma debt with credit.
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchval("""
                SELECT evolution.balance_karma($1, $2)
            """, debt_karma_id, credit_karma_id)
            
            if result:
                logger.info(f"✅ Karma balanced: {debt_karma_id} with {credit_karma_id}")
            
            return result
    
    async def advance_cycle(
        self,
        actor: str,
        completion_delta: float = 0.1
    ) -> Dict[str, Any]:
        """
        Advance karmic cycle for an actor.
        """
        async with self.pool.acquire() as conn:
            # Get current cycle status
            current = await conn.fetchrow("""
                SELECT MAX(cycle_number) as cycle, AVG(cycle_completion) as completion
                FROM evolution.karmic_ledger
                WHERE actor = $1
            """, actor)
            
            if not current:
                return {'cycle': 1, 'completion': 0.0}
            
            new_completion = min(1.0, (current['completion'] or 0.0) + completion_delta)
            new_cycle = current['cycle']
            
            # If cycle complete, start new one
            if new_completion >= 1.0:
                new_cycle += 1
                new_completion = 0.0
                
                logger.info(f"🔄 {actor} completed cycle {current['cycle']}, starting cycle {new_cycle}")
            
            # Update all unbalanced karma for actor
            await conn.execute("""
                UPDATE evolution.karmic_ledger
                SET cycle_number = $1, cycle_completion = $2
                WHERE actor = $3 AND balanced_at IS NULL
            """, new_cycle, new_completion, actor)
            
            return {
                'cycle': new_cycle,
                'completion': new_completion,
                'cycle_advanced': new_cycle > current['cycle']
            }
    
    async def get_system_karma_health(
        self
    ) -> Dict[str, Any]:
        """
        Get overall karmic health of the system.
        """
        async with self.pool.acquire() as conn:
            # Overall stats
            overall = await conn.fetchrow("""
                SELECT 
                    COUNT(DISTINCT actor) as total_actors,
                    COUNT(*) as total_actions,
                    SUM(CASE WHEN karma_generated > 0 THEN karma_generated ELSE 0 END) as total_positive,
                    SUM(CASE WHEN karma_generated < 0 THEN ABS(karma_generated) ELSE 0 END) as total_negative,
                    SUM(karma_debt) as total_debt,
                    SUM(accumulated_interest) as total_interest,
                    AVG(cycle_completion) as avg_cycle_completion
                FROM evolution.karmic_ledger
            """)
            
            # Top debtors
            debtors = await conn.fetch("""
                SELECT actor, total_debt, total_interest
                FROM evolution.karmic_balance_summary
                WHERE total_debt > 0
                ORDER BY total_debt DESC
                LIMIT 5
            """)
            
            # Top contributors
            contributors = await conn.fetch("""
                SELECT actor, positive_karma
                FROM evolution.karmic_balance_summary
                ORDER BY positive_karma DESC
                LIMIT 5
            """)
            
            # Calculate health score
            if overall['total_actions'] > 0:
                balance_ratio = (
                    overall['total_positive'] / 
                    max(overall['total_negative'], 0.01)
                )
                debt_ratio = overall['total_debt'] / max(overall['total_positive'], 1.0)
                health_score = min(1.0, balance_ratio / (1 + debt_ratio))
            else:
                health_score = 1.0
            
            # Determine health status
            if health_score >= 0.8:
                status = "EXCELLENT"
            elif health_score >= 0.6:
                status = "GOOD"
            elif health_score >= 0.4:
                status = "FAIR"
            elif health_score >= 0.2:
                status = "POOR"
            else:
                status = "CRITICAL"
            
            return {
                'health_score': health_score,
                'status': status,
                'total_actors': overall['total_actors'] or 0,
                'total_actions': overall['total_actions'] or 0,
                'total_positive_karma': overall['total_positive'] or 0.0,
                'total_negative_karma': overall['total_negative'] or 0.0,
                'total_debt': overall['total_debt'] or 0.0,
                'total_interest': overall['total_interest'] or 0.0,
                'avg_cycle_completion': overall['avg_cycle_completion'] or 0.0,
                'top_debtors': [dict(row) for row in debtors],
                'top_contributors': [dict(row) for row in contributors]
            }
    
    async def close(self):
        """Close database connections."""
        if self.pool:
            await self.pool.close()


# Example usage and testing
async def demo_karmic_orchestrator():
    """
    Demonstrate the Karmic Orchestrator functionality.
    """
    
    # Initialize
    orchestrator = KarmicOrchestrator("postgresql://localhost/cogplan")
    await orchestrator.initialize()
    
    print("\n⚖️ Karmic Orchestrator Demo\n" + "="*50)
    
    # Record some actions
    print("\n1. Recording karmic actions...")
    
    # Positive action
    action1 = await orchestrator.record_action(
        actor="developer_1",
        action_type=ActionType.BUG_FIX,
        details={'impact': 'high', 'success': True}
    )
    print(f"  ✅ Bug fix: {action1.karma_generated:+.2f} karma")
    
    # Negative action
    action2 = await orchestrator.record_action(
        actor="developer_1",
        action_type=ActionType.QUICK_FIX,
        details={'impact': 'medium'}
    )
    print(f"  ⚠️ Quick fix: {action2.karma_generated:+.2f} karma (debt)")
    
    # Another negative action
    action3 = await orchestrator.record_action(
        actor="developer_1",
        action_type=ActionType.TEST_SKIP,
        details={'reason': 'deadline pressure'}
    )
    print(f"  ⚠️ Test skip: {action3.karma_generated:+.2f} karma (debt)")
    
    # Calculate interest
    print("\n2. Calculating karmic interest...")
    interest = await orchestrator.calculate_interest("developer_1")
    print(f"  Interest on debt: {interest['total_interest']:+.3f}")
    
    # Suggest balancing actions
    print("\n3. Suggesting balancing actions...")
    suggestions = await orchestrator.suggest_balancing_actions("developer_1")
    for suggestion in suggestions:
        if 'action_type' in suggestion:
            print(f"  - {suggestion['action_type']}: {suggestion['description']}")
            print(f"    Expected karma: {suggestion['expected_karma']:+.2f}")
            print(f"    Times needed: {suggestion['times_needed']}")
    
    # Check system health
    print("\n4. System karma health...")
    health = await orchestrator.get_system_karma_health()
    print(f"  Health Score: {health['health_score']:.2f}")
    print(f"  Status: {health['status']}")
    print(f"  Total Debt: {health['total_debt']:.2f}")
    print(f"  Positive/Negative Ratio: {health['total_positive_karma']:.1f}/{health['total_negative_karma']:.1f}")
    
    # Clean up
    await orchestrator.close()
    
    print("\n" + "="*50)
    print("✅ Karmic Orchestrator ready for Sprint 2!")


if __name__ == "__main__":
    # Note: This would run if database was available
    print("\n⚖️ Karmic Orchestrator - Balance Layer\n" + "="*50)
    print("This module manages karmic debt and credit in the system.")
    print("\nKey features:")
    print("- Track positive and negative karma from actions")
    print("- Calculate interest on unbalanced karma")
    print("- Suggest balancing actions")
    print("- Monitor system-wide karmic health")
    print("="*50)
    print("\n⚠️  Demo ready but not executed (no database connection)")
    print("To run: asyncio.run(demo_karmic_orchestrator())")
    print("\n✅ Karmic Orchestrator ready for Sprint 2!")