#!/usr/bin/env python3
"""
@cognimap:fingerprint
id: 659a3353-0c5e-4cdb-9e3d-d626bfe66a87
birth: 2025-08-07T07:23:38.093923Z
parent: None
intent: Polarity Calculator - The Feeling Layer of the Aether Protocol
semantic_tags: [database, api, testing, utility, configuration]
version: 1.0.0
last_sync: 2025-08-07T07:23:38.094659Z
hash: fbf066dd
language: python
type: component
@end:cognimap
"""

"""
Polarity Calculator - The Feeling Layer of the Aether Protocol

This module implements Sprint 1: Foundation of Feeling, replacing the binary
garbage flag with a continuous polarity spectrum from -1.0 to +1.0.

Polarity represents the quality/outcome of an event:
- -1.0: Complete failure, destructive
- -0.5: Significant problems
-  0.0: Neutral
- +0.5: Good progress
- +1.0: Perfect success, constructive
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from datetime import datetime
import json


class PolarityFactors(Enum):
    """Factors that influence polarity calculation."""
    SUCCESS = "success"          # Did the action succeed?
    EFFICIENCY = "efficiency"    # How efficient was it?
    IMPACT = "impact"           # What was the impact?
    ALIGNMENT = "alignment"     # How aligned with intent?
    QUALITY = "quality"         # Quality of output
    COST = "cost"              # Resource cost
    TIME = "time"              # Time taken
    ERRORS = "errors"          # Error count


class PolarityCalculator:
    """
    Calculates polarity scores for events based on multiple factors.
    
    This replaces the binary garbage flag with a nuanced spectrum that
    captures the actual quality and outcome of system events.
    """
    
    def __init__(self):
        # Sentiment words for text analysis
        self.positive_indicators = {
            'success', 'complete', 'passed', 'created', 'improved',
            'optimized', 'fixed', 'resolved', 'achieved', 'delivered',
            'enhanced', 'upgraded', 'implemented', 'deployed', 'merged'
        }
        
        self.negative_indicators = {
            'failed', 'error', 'broken', 'crashed', 'timeout', 'rejected',
            'blocked', 'stuck', 'corrupted', 'lost', 'deprecated',
            'rollback', 'reverted', 'conflict', 'deadlock', 'leak'
        }
        
        # Event type base polarities
        self.event_type_polarities = {
            'completion': 0.7,
            'success': 0.8,
            'created': 0.6,
            'updated': 0.4,
            'error': -0.7,
            'failure': -0.8,
            'warning': -0.2,
            'info': 0.1,
            'debug': 0.0,
            'rollback': -0.6,
            'retry': -0.3,
            'timeout': -0.5
        }
        
        # Agent-specific weight adjustments
        self.agent_weights = {
            'planner': {'alignment': 1.5, 'quality': 1.2},
            'codegen': {'quality': 1.5, 'errors': 1.3},
            'tester': {'success': 1.5, 'errors': 1.5},
            'implementor': {'impact': 1.5, 'efficiency': 1.2},
            'treasurer': {'cost': 2.0, 'efficiency': 1.5},
            'architect': {'alignment': 1.5, 'quality': 1.3}
        }
    
    def calculate_polarity(self, event: Dict[str, Any]) -> float:
        """
        Calculate polarity score for an event.
        
        Args:
            event: Event dictionary containing type, agent, payload, etc.
            
        Returns:
            Polarity score from -1.0 to +1.0
        """
        factors = self._extract_factors(event)
        weights = self._get_weights(event.get('agent', 'unknown'))
        
        # Calculate weighted score
        total_score = 0.0
        total_weight = 0.0
        
        for factor, value in factors.items():
            weight = weights.get(factor.value, 1.0)
            total_score += value * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Normalize to [-1, 1]
        raw_score = total_score / total_weight
        return max(-1.0, min(1.0, raw_score))
    
    def calculate_from_payload(self, payload: Dict[str, Any]) -> float:
        """
        Calculate polarity directly from payload data.
        
        Useful for real-time polarity calculation without full event context.
        """
        score = 0.0
        
        # Check explicit success/failure
        if 'success' in payload:
            score += 0.8 if payload['success'] else -0.8
        
        # Check for errors
        if 'error' in payload or 'errors' in payload:
            error_count = len(payload.get('errors', [])) or 1
            score -= min(0.5, error_count * 0.1)
        
        # Check performance metrics
        if 'duration' in payload and 'expected_duration' in payload:
            efficiency = payload['expected_duration'] / max(payload['duration'], 0.001)
            score += (efficiency - 1.0) * 0.2  # Bonus/penalty for speed
        
        # Check test results
        if 'tests_passed' in payload and 'tests_total' in payload:
            if payload['tests_total'] > 0:
                pass_rate = payload['tests_passed'] / payload['tests_total']
                score += (pass_rate - 0.5) * 0.6  # -0.3 to +0.3 based on pass rate
        
        # Check coverage
        if 'coverage' in payload:
            coverage = payload['coverage']
            if coverage >= 80:
                score += 0.2
            elif coverage >= 60:
                score += 0.1
            elif coverage < 40:
                score -= 0.2
        
        return max(-1.0, min(1.0, score))
    
    def calculate_from_text(self, text: str) -> float:
        """
        Calculate polarity from text content using sentiment analysis.
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Count positive and negative indicators
        positive_count = sum(1 for word in self.positive_indicators if word in text_lower)
        negative_count = sum(1 for word in self.negative_indicators if word in text_lower)
        
        # Calculate base score
        if positive_count + negative_count == 0:
            return 0.0
        
        score = (positive_count - negative_count) / (positive_count + negative_count)
        
        # Adjust for intensity words
        if 'critical' in text_lower or 'severe' in text_lower:
            score *= 1.5
        if 'minor' in text_lower or 'small' in text_lower:
            score *= 0.5
        
        return max(-1.0, min(1.0, score))
    
    def _extract_factors(self, event: Dict[str, Any]) -> Dict[PolarityFactors, float]:
        """
        Extract polarity factors from event.
        """
        factors = {}
        payload = event.get('payload', {})
        event_type = event.get('type', '')
        
        # Success factor
        if 'success' in payload:
            factors[PolarityFactors.SUCCESS] = 1.0 if payload['success'] else -1.0
        elif event_type in self.event_type_polarities:
            factors[PolarityFactors.SUCCESS] = self.event_type_polarities[event_type]
        
        # Efficiency factor
        if 'duration' in payload and 'expected_duration' in payload:
            efficiency = payload['expected_duration'] / max(payload['duration'], 0.001)
            factors[PolarityFactors.EFFICIENCY] = min(1.0, efficiency) * 2 - 1  # Map to [-1, 1]
        
        # Impact factor
        if 'changes_made' in payload:
            impact = min(payload['changes_made'] / 10, 1.0)  # Normalize to [0, 1]
            factors[PolarityFactors.IMPACT] = impact * 2 - 1
        
        # Quality factor from tests
        if 'tests_passed' in payload and 'tests_total' in payload:
            if payload['tests_total'] > 0:
                quality = payload['tests_passed'] / payload['tests_total']
                factors[PolarityFactors.QUALITY] = quality * 2 - 1
        
        # Cost factor
        if 'cost' in payload and 'budget' in payload:
            if payload['budget'] > 0:
                cost_ratio = payload['cost'] / payload['budget']
                factors[PolarityFactors.COST] = 1.0 - cost_ratio  # Under budget is positive
        
        # Error factor
        if 'errors' in payload:
            error_count = len(payload.get('errors', []))
            factors[PolarityFactors.ERRORS] = -min(1.0, error_count * 0.2)
        
        # Text sentiment as additional factor
        if 'message' in payload:
            text_polarity = self.calculate_from_text(payload['message'])
            factors[PolarityFactors.ALIGNMENT] = text_polarity
        
        return factors
    
    def _get_weights(self, agent: str) -> Dict[str, float]:
        """
        Get weight adjustments for specific agent.
        """
        base_weights = {
            PolarityFactors.SUCCESS.value: 1.0,
            PolarityFactors.EFFICIENCY.value: 0.8,
            PolarityFactors.IMPACT.value: 0.9,
            PolarityFactors.ALIGNMENT.value: 0.7,
            PolarityFactors.QUALITY.value: 1.0,
            PolarityFactors.COST.value: 0.6,
            PolarityFactors.TIME.value: 0.5,
            PolarityFactors.ERRORS.value: 1.2
        }
        
        # Apply agent-specific adjustments
        if agent in self.agent_weights:
            for factor, weight in self.agent_weights[agent].items():
                base_weights[factor] = weight
        
        return base_weights
    
    def suggest_polarity_improvement(self, current_polarity: float, factors: Dict[str, float]) -> List[str]:
        """
        Suggest actions to improve polarity score.
        """
        suggestions = []
        
        if current_polarity < 0:
            # Negative polarity - focus on fixing problems
            if factors.get('errors', 0) < 0:
                suggestions.append("Fix errors and exceptions")
            if factors.get('success', 0) < 0:
                suggestions.append("Investigate and resolve failures")
            if factors.get('efficiency', 0) < 0:
                suggestions.append("Optimize performance and reduce timeouts")
        
        elif current_polarity < 0.5:
            # Low positive - improve quality
            if factors.get('quality', 1) < 0.7:
                suggestions.append("Improve test coverage and code quality")
            if factors.get('alignment', 1) < 0.5:
                suggestions.append("Better align with system intents")
        
        else:
            # Good polarity - optimize further
            suggestions.append("Maintain current performance")
            if factors.get('efficiency', 1) < 0.8:
                suggestions.append("Further optimize efficiency")
        
        return suggestions
    
    def get_polarity_interpretation(self, polarity: float) -> Tuple[str, str]:
        """
        Get human-readable interpretation of polarity score.
        
        Returns:
            Tuple of (level, description)
        """
        if polarity >= 0.8:
            return ("EXCELLENT", "Outstanding performance, highly constructive")
        elif polarity >= 0.5:
            return ("GOOD", "Positive outcome, meeting expectations")
        elif polarity >= 0.2:
            return ("ACCEPTABLE", "Adequate performance, room for improvement")
        elif polarity >= -0.2:
            return ("NEUTRAL", "Mixed results, neither positive nor negative")
        elif polarity >= -0.5:
            return ("POOR", "Below expectations, needs attention")
        elif polarity >= -0.8:
            return ("CRITICAL", "Significant issues, immediate action required")
        else:
            return ("FAILURE", "Complete failure, system breakdown")


class PolarityThreshold:
    """
    Manages polarity thresholds for different contexts.
    """
    
    def __init__(self):
        self.default_threshold = -0.5  # Events below this are filtered
        
        # Context-specific thresholds
        self.context_thresholds = {
            'production': -0.3,    # Stricter in production
            'development': -0.6,   # More lenient in dev
            'testing': -0.7,       # Very lenient in testing
            'critical_path': -0.2  # Very strict for critical operations
        }
    
    def should_process(self, polarity: float, context: str = 'default') -> bool:
        """
        Determine if an event should be processed based on polarity.
        """
        threshold = self.context_thresholds.get(context, self.default_threshold)
        return polarity > threshold
    
    def get_quality_band(self, polarity: float) -> str:
        """
        Get quality band for polarity score.
        """
        if polarity >= 0.7:
            return "HIGH_QUALITY"
        elif polarity >= 0.3:
            return "MEDIUM_QUALITY"
        elif polarity >= -0.3:
            return "LOW_QUALITY"
        else:
            return "GARBAGE"


# Standalone utility functions
def migrate_garbage_to_polarity(has_garbage_flag: bool) -> float:
    """
    Migrate from binary garbage flag to polarity spectrum.
    """
    return -0.8 if has_garbage_flag else 0.5


def calculate_aggregate_polarity(polarities: List[float]) -> float:
    """
    Calculate aggregate polarity for multiple events.
    """
    if not polarities:
        return 0.0
    
    # Weighted average giving more weight to extreme values
    weighted_sum = 0.0
    weight_sum = 0.0
    
    for p in polarities:
        weight = abs(p) + 0.5  # Weight by extremity
        weighted_sum += p * weight
        weight_sum += weight
    
    return weighted_sum / weight_sum if weight_sum > 0 else 0.0


# Example usage and testing
if __name__ == "__main__":
    # Initialize calculator
    calc = PolarityCalculator()
    threshold = PolarityThreshold()
    
    # Test different event types
    test_events = [
        {
            "type": "completion",
            "agent": "planner",
            "payload": {
                "success": True,
                "message": "Successfully created plan for API implementation",
                "duration": 2.5,
                "expected_duration": 3.0
            }
        },
        {
            "type": "error",
            "agent": "codegen",
            "payload": {
                "success": False,
                "message": "Failed to generate code due to syntax error",
                "errors": ["SyntaxError", "ImportError"]
            }
        },
        {
            "type": "test_result",
            "agent": "tester",
            "payload": {
                "tests_passed": 45,
                "tests_total": 50,
                "coverage": 75,
                "message": "Most tests passed with good coverage"
            }
        }
    ]
    
    print("\n🎭 Polarity Spectrum Testing\n" + "="*50)
    
    for i, event in enumerate(test_events, 1):
        polarity = calc.calculate_polarity(event)
        level, description = calc.get_polarity_interpretation(polarity)
        quality = threshold.get_quality_band(polarity)
        should_process = threshold.should_process(polarity)
        
        print(f"\nEvent {i}: {event['type']} from {event['agent']}")
        print(f"  Polarity: {polarity:+.3f}")
        print(f"  Level: {level}")
        print(f"  Description: {description}")
        print(f"  Quality Band: {quality}")
        print(f"  Should Process: {should_process}")
    
    # Test migration from garbage flag
    print("\n" + "="*50)
    print("Migration from garbage flag:")
    print(f"  garbage=True  → polarity={migrate_garbage_to_polarity(True):+.3f}")
    print(f"  garbage=False → polarity={migrate_garbage_to_polarity(False):+.3f}")
    
    # Test aggregate polarity
    polarities = [0.8, 0.6, -0.2, 0.9, -0.1]
    print(f"\nAggregate polarity of {polarities}:")
    print(f"  Result: {calculate_aggregate_polarity(polarities):+.3f}")
    
    print("\n✅ Polarity Calculator ready for Sprint 1!")