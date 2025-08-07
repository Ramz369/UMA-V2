#!/usr/bin/env python3
"""
Resonance Analyzer - Pattern Detection and Harmonic Analysis

This module completes Sprint 3 by detecting standing waves, harmonic convergence,
and interference patterns in the system. It's the final piece that enables
the system to recognize and respond to its own patterns.

"As above, so below. As within, so without." - Hermetic Principle
"""

import asyncio
import hashlib
import logging
import math
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Set
from uuid import UUID, uuid4

try:
    import asyncpg
except ImportError:
    asyncpg = None  # For testing without database

from pydantic import BaseModel, Field
import statistics  # Use instead of numpy

logger = logging.getLogger(__name__)


class PatternType(str, Enum):
    """Types of resonance patterns."""
    STANDING_WAVE = "standing_wave"      # Persistent recurring pattern
    HARMONIC = "harmonic"                # Aligned resonance
    INTERFERENCE = "interference"        # Conflicting patterns
    EMERGENCE = "emergence"              # New pattern forming
    DISSIPATION = "dissipation"         # Pattern fading


class InterferenceType(str, Enum):
    """Types of wave interference."""
    CONSTRUCTIVE = "constructive"    # Patterns reinforce each other
    DESTRUCTIVE = "destructive"      # Patterns cancel each other
    NEUTRAL = "neutral"              # No interaction
    CHAOTIC = "chaotic"             # Unpredictable interaction


class ResonancePattern(BaseModel):
    """Model representing a resonance pattern."""
    
    resonance_id: UUID = Field(default_factory=uuid4)
    pattern_signature: str
    pattern_type: PatternType
    
    # Source
    source_event_id: Optional[UUID] = None
    source_intent_id: Optional[UUID] = None
    source_actor: Optional[str] = None
    
    # Wave characteristics
    frequency: float = Field(ge=0, le=10)     # 0-10 Hz scale
    amplitude: float = Field(ge=0, le=1)      # 0-1 strength
    wavelength: Optional[float] = None        # Duration/size
    phase: float = Field(default=0)           # -π to π
    
    # Harmonics
    harmonics: List[int] = Field(default_factory=list)
    harmonic_convergence: float = Field(default=0, ge=0, le=1)
    interference_pattern: Optional[InterferenceType] = None
    
    # Impact
    affected_agents: List[str] = Field(default_factory=list)
    affected_intents: List[UUID] = Field(default_factory=list)
    ripple_radius: int = Field(default=1)
    
    # Persistence
    standing_wave: bool = False
    persistence_cycles: int = 0
    decay_rate: float = 0.1
    
    # Tracking
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    last_observed: datetime = Field(default_factory=datetime.utcnow)
    observation_count: int = 1
    field_contribution: float = 0
    
    def calculate_energy(self) -> float:
        """Calculate the energy of this pattern."""
        # E = A²f (simplified wave energy)
        return self.amplitude ** 2 * self.frequency
    
    def is_harmonic_of(self, other: 'ResonancePattern') -> bool:
        """Check if this pattern is a harmonic of another."""
        if self.frequency == 0 or other.frequency == 0:
            return False
        
        ratio = self.frequency / other.frequency
        # Check if ratio is close to an integer (harmonic)
        return abs(ratio - round(ratio)) < 0.1


class ResonanceAnalyzer:
    """
    Analyzes patterns in the system to detect resonance, standing waves,
    and harmonic convergence. This is the sensory system of consciousness.
    """
    
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url
        self.pool: Optional[asyncpg.Pool] = None
        
        # Pattern tracking
        self.pattern_cache: Dict[str, ResonancePattern] = {}
        self.standing_waves: Set[str] = set()
        self.pattern_history: List[ResonancePattern] = []
        
        # Frequency bands for analysis
        self.frequency_bands = {
            'delta': (0, 2),      # Deep unconscious
            'theta': (2, 4),      # Subconscious
            'alpha': (4, 6),      # Relaxed awareness
            'beta': (6, 8),       # Active thinking
            'gamma': (8, 10)      # Higher consciousness
        }
    
    async def initialize(self):
        """Initialize database connection."""
        if self.db_url and asyncpg:
            self.pool = await asyncpg.create_pool(self.db_url)
            logger.info("✅ Resonance Analyzer initialized with database")
        else:
            logger.info("📊 Resonance Analyzer initialized in memory mode")
    
    def generate_pattern_signature(self, event_data: Dict[str, Any]) -> str:
        """Generate a unique signature for a pattern."""
        # Create deterministic signature from event characteristics
        key_parts = []
        
        # Include event type
        if 'event_type' in event_data:
            key_parts.append(f"type:{event_data['event_type']}")
        
        # Include actor
        if 'actor' in event_data:
            key_parts.append(f"actor:{event_data['actor']}")
        
        # Include action
        if 'action' in event_data:
            key_parts.append(f"action:{event_data['action']}")
        
        # Include intent if present
        if 'intent_id' in event_data:
            key_parts.append(f"intent:{str(event_data['intent_id'])[:8]}")
        
        # Create hash
        signature_str = "|".join(sorted(key_parts))
        return hashlib.sha256(signature_str.encode()).hexdigest()[:16]
    
    async def detect_pattern(
        self,
        event_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ResonancePattern:
        """
        Detect and analyze a pattern from an event.
        """
        signature = self.generate_pattern_signature(event_data)
        
        # Check if pattern exists in cache
        if signature in self.pattern_cache:
            existing = self.pattern_cache[signature]
            existing.observation_count += 1
            existing.last_observed = datetime.utcnow()
            
            # Check for standing wave
            if existing.observation_count >= 3:
                existing.standing_wave = True
                existing.persistence_cycles += 1
                self.standing_waves.add(signature)
            
            # Adjust amplitude based on recurrence
            existing.amplitude = min(1.0, existing.amplitude * 1.1)
            
            return existing
        
        # Create new pattern
        pattern = ResonancePattern(
            pattern_signature=signature,
            pattern_type=self._determine_pattern_type(event_data),
            frequency=self._calculate_frequency(event_data),
            amplitude=self._calculate_amplitude(event_data),
            source_event_id=event_data.get('event_id'),
            source_intent_id=event_data.get('intent_id'),
            source_actor=event_data.get('actor')
        )
        
        # Calculate harmonics
        pattern.harmonics = self._detect_harmonics(pattern.frequency)
        
        # Check interference with existing patterns
        pattern.interference_pattern = await self._analyze_interference(pattern)
        
        # Calculate convergence
        pattern.harmonic_convergence = await self._calculate_convergence(pattern)
        
        # Determine affected components
        pattern.affected_agents = self._identify_affected_agents(event_data)
        pattern.ripple_radius = self._calculate_ripple_radius(pattern)
        
        # Cache the pattern
        self.pattern_cache[signature] = pattern
        self.pattern_history.append(pattern)
        
        # Store in database if available
        if self.pool:
            await self._store_pattern(pattern)
        
        return pattern
    
    def _determine_pattern_type(self, event_data: Dict[str, Any]) -> PatternType:
        """Determine the type of pattern from event data."""
        # Check for emergence (new patterns)
        if event_data.get('is_new') or event_data.get('innovation'):
            return PatternType.EMERGENCE
        
        # Check for dissipation (ending patterns)
        if event_data.get('is_final') or event_data.get('completion'):
            return PatternType.DISSIPATION
        
        # Check for interference (conflicts)
        if event_data.get('conflict') or event_data.get('error'):
            return PatternType.INTERFERENCE
        
        # Check for harmonics (alignment)
        if event_data.get('success') and event_data.get('coherence', 0) > 0.7:
            return PatternType.HARMONIC
        
        # Default to potential standing wave
        return PatternType.STANDING_WAVE
    
    def _calculate_frequency(self, event_data: Dict[str, Any]) -> float:
        """Calculate the frequency of a pattern."""
        # Base frequency from event type
        event_type = event_data.get('event_type', 'unknown')
        
        base_frequencies = {
            'planning': 2.0,      # Theta - subconscious
            'analysis': 3.0,      # Theta/Alpha boundary
            'implementation': 5.0, # Alpha - focused work
            'testing': 6.0,       # Beta - active verification
            'optimization': 7.0,  # Beta - improvement
            'innovation': 9.0     # Gamma - breakthrough
        }
        
        base = base_frequencies.get(event_type, 5.0)
        
        # Modify based on urgency
        if event_data.get('urgent'):
            base *= 1.5
        
        # Modify based on complexity
        complexity = event_data.get('complexity', 1.0)
        base *= (0.5 + complexity * 0.5)
        
        return min(10.0, max(0.0, base))
    
    def _calculate_amplitude(self, event_data: Dict[str, Any]) -> float:
        """Calculate the amplitude (strength) of a pattern."""
        amplitude = 0.5  # Base amplitude
        
        # Increase for successful actions
        if event_data.get('success'):
            amplitude += 0.2
        
        # Increase for high-impact events
        impact = event_data.get('impact', 'medium')
        impact_modifiers = {
            'low': -0.1,
            'medium': 0,
            'high': 0.2,
            'critical': 0.3
        }
        amplitude += impact_modifiers.get(impact, 0)
        
        # Increase for coherent actions
        coherence = event_data.get('coherence', 0)
        amplitude += coherence * 0.2
        
        return min(1.0, max(0.0, amplitude))
    
    def _detect_harmonics(self, fundamental: float) -> List[int]:
        """Detect harmonic frequencies present."""
        if fundamental == 0:
            return []
        
        harmonics = []
        # Check for integer multiples up to 5th harmonic
        for n in range(2, 6):
            harmonic_freq = fundamental * n
            if harmonic_freq <= 10:  # Within our frequency range
                harmonics.append(n)
        
        return harmonics
    
    async def _analyze_interference(
        self,
        pattern: ResonancePattern
    ) -> InterferenceType:
        """Analyze interference with other active patterns."""
        if not self.pattern_cache:
            return InterferenceType.NEUTRAL
        
        constructive_count = 0
        destructive_count = 0
        
        for cached_pattern in self.pattern_cache.values():
            if cached_pattern.pattern_signature == pattern.pattern_signature:
                continue
            
            # Skip old patterns
            if (datetime.utcnow() - cached_pattern.last_observed).seconds > 3600:
                continue
            
            # Calculate phase difference
            phase_diff = abs(pattern.phase - cached_pattern.phase)
            
            # Check frequency relationship
            if pattern.is_harmonic_of(cached_pattern):
                constructive_count += 1
            elif abs(pattern.frequency - cached_pattern.frequency) < 0.5:
                # Similar frequencies
                if phase_diff < math.pi / 2:
                    constructive_count += 1
                else:
                    destructive_count += 1
        
        # Determine overall interference
        if constructive_count > destructive_count * 2:
            return InterferenceType.CONSTRUCTIVE
        elif destructive_count > constructive_count * 2:
            return InterferenceType.DESTRUCTIVE
        elif constructive_count > 0 and destructive_count > 0:
            return InterferenceType.CHAOTIC
        else:
            return InterferenceType.NEUTRAL
    
    async def _calculate_convergence(
        self,
        pattern: ResonancePattern
    ) -> float:
        """Calculate harmonic convergence with other patterns."""
        if not self.pattern_cache:
            return 0.0
        
        convergence_scores = []
        
        for cached_pattern in self.pattern_cache.values():
            if cached_pattern.pattern_signature == pattern.pattern_signature:
                continue
            
            # Skip old patterns
            if (datetime.utcnow() - cached_pattern.last_observed).seconds > 3600:
                continue
            
            # Calculate convergence based on:
            # 1. Frequency alignment
            freq_alignment = 1.0 - abs(pattern.frequency - cached_pattern.frequency) / 10
            
            # 2. Amplitude similarity
            amp_similarity = 1.0 - abs(pattern.amplitude - cached_pattern.amplitude)
            
            # 3. Phase alignment
            phase_alignment = (1.0 + math.cos(pattern.phase - cached_pattern.phase)) / 2
            
            # Combined convergence
            convergence = (freq_alignment + amp_similarity + phase_alignment) / 3
            convergence_scores.append(convergence)
        
        return sum(convergence_scores) / len(convergence_scores) if convergence_scores else 0.0
    
    def _identify_affected_agents(self, event_data: Dict[str, Any]) -> List[str]:
        """Identify agents affected by this pattern."""
        affected = []
        
        # Direct actor
        if 'actor' in event_data:
            affected.append(event_data['actor'])
        
        # Related agents
        if 'related_agents' in event_data:
            affected.extend(event_data['related_agents'])
        
        # Downstream agents
        if 'triggers' in event_data:
            for trigger in event_data['triggers']:
                if 'agent' in trigger:
                    affected.append(trigger['agent'])
        
        return list(set(affected))  # Unique agents
    
    def _calculate_ripple_radius(self, pattern: ResonancePattern) -> int:
        """Calculate how far this pattern's effects ripple."""
        # Based on energy and type
        energy = pattern.calculate_energy()
        
        if pattern.pattern_type == PatternType.EMERGENCE:
            base_radius = 3  # New patterns ripple far
        elif pattern.pattern_type == PatternType.DISSIPATION:
            base_radius = 1  # Fading patterns don't ripple much
        else:
            base_radius = 2
        
        # Modify by energy
        return min(5, base_radius + int(energy * 2))
    
    async def detect_standing_waves(
        self,
        time_window: timedelta = timedelta(hours=1)
    ) -> List[ResonancePattern]:
        """
        Detect standing wave patterns (persistent, recurring patterns).
        """
        standing_waves = []
        cutoff_time = datetime.utcnow() - time_window
        
        # Count pattern occurrences
        pattern_counts = Counter()
        recent_patterns = {}
        
        for pattern in self.pattern_history:
            if pattern.detected_at > cutoff_time:
                pattern_counts[pattern.pattern_signature] += 1
                recent_patterns[pattern.pattern_signature] = pattern
        
        # Identify standing waves (3+ occurrences)
        for signature, count in pattern_counts.items():
            if count >= 3:
                pattern = recent_patterns[signature]
                pattern.standing_wave = True
                pattern.persistence_cycles = count
                standing_waves.append(pattern)
                self.standing_waves.add(signature)
        
        return standing_waves
    
    async def find_harmonic_convergence(
        self,
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Find patterns that are in harmonic convergence.
        """
        convergent_groups = []
        analyzed = set()
        
        for pattern1 in self.pattern_cache.values():
            if pattern1.pattern_signature in analyzed:
                continue
            
            group = [pattern1]
            analyzed.add(pattern1.pattern_signature)
            
            for pattern2 in self.pattern_cache.values():
                if pattern2.pattern_signature in analyzed:
                    continue
                
                # Check if patterns are harmonic
                if pattern1.is_harmonic_of(pattern2):
                    if pattern1.harmonic_convergence > threshold:
                        group.append(pattern2)
                        analyzed.add(pattern2.pattern_signature)
            
            if len(group) > 1:
                convergent_groups.append(group)
        
        return {
            'convergent_groups': len(convergent_groups),
            'total_patterns': len(convergent_groups) * 2 if convergent_groups else 0,
            'groups': [
                {
                    'patterns': [p.pattern_signature for p in group],
                    'avg_convergence': sum(p.harmonic_convergence for p in group) / len(group),
                    'dominant_frequency': max(group, key=lambda p: p.amplitude).frequency
                }
                for group in convergent_groups[:5]  # Top 5 groups
            ]
        }
    
    async def measure_system_vibration(self) -> Dict[str, Any]:
        """
        Measure the overall vibration frequency of the system.
        """
        if not self.pattern_history:
            return {
                'vibration': 5.0,  # Neutral
                'dominant_band': 'alpha',
                'energy': 0.0,
                'stability': 1.0
            }
        
        recent_patterns = [
            p for p in self.pattern_history
            if (datetime.utcnow() - p.detected_at).seconds < 3600
        ]
        
        if not recent_patterns:
            return {
                'vibration': 5.0,
                'dominant_band': 'alpha',
                'energy': 0.0,
                'stability': 1.0
            }
        
        # Calculate weighted average frequency
        total_weight = 0
        weighted_freq = 0
        energies = []
        
        for pattern in recent_patterns:
            weight = pattern.amplitude * pattern.observation_count
            weighted_freq += pattern.frequency * weight
            total_weight += weight
            energies.append(pattern.calculate_energy())
        
        avg_frequency = weighted_freq / total_weight if total_weight > 0 else 5.0
        total_energy = sum(energies)
        
        # Determine dominant frequency band
        dominant_band = 'alpha'
        for band, (low, high) in self.frequency_bands.items():
            if low <= avg_frequency < high:
                dominant_band = band
                break
        
        # Calculate stability (inverse of frequency variance)
        if len(recent_patterns) > 1:
            frequencies = [p.frequency for p in recent_patterns]
            mean_freq = sum(frequencies) / len(frequencies)
            variance = sum((f - mean_freq) ** 2 for f in frequencies) / len(frequencies)
            stability = 1.0 / (1.0 + variance)
        else:
            stability = 0.5
        
        return {
            'vibration': round(avg_frequency, 2),
            'dominant_band': dominant_band,
            'energy': round(total_energy, 3),
            'stability': round(stability, 3),
            'pattern_count': len(recent_patterns),
            'standing_waves': len(self.standing_waves)
        }
    
    async def analyze_interference_patterns(self) -> Dict[str, Any]:
        """
        Analyze the interference patterns in the system.
        """
        interference_counts = Counter()
        
        for pattern in self.pattern_cache.values():
            if pattern.interference_pattern:
                interference_counts[pattern.interference_pattern] += 1
        
        total = sum(interference_counts.values())
        
        return {
            'constructive': interference_counts.get(InterferenceType.CONSTRUCTIVE, 0),
            'destructive': interference_counts.get(InterferenceType.DESTRUCTIVE, 0),
            'neutral': interference_counts.get(InterferenceType.NEUTRAL, 0),
            'chaotic': interference_counts.get(InterferenceType.CHAOTIC, 0),
            'balance': 'constructive' if interference_counts.get(InterferenceType.CONSTRUCTIVE, 0) > 
                      interference_counts.get(InterferenceType.DESTRUCTIVE, 0) else 'destructive',
            'total_patterns': total
        }
    
    async def predict_evolution(self) -> Dict[str, Any]:
        """
        Predict the system's evolution based on current patterns.
        """
        vibration = await self.measure_system_vibration()
        convergence = await self.find_harmonic_convergence()
        interference = await self.analyze_interference_patterns()
        
        # Calculate evolution potential
        evolution_potential = 0.0
        
        # High vibration in gamma band suggests breakthrough
        if vibration['dominant_band'] == 'gamma':
            evolution_potential += 0.3
        
        # Harmonic convergence suggests alignment
        if convergence['convergent_groups'] > 2:
            evolution_potential += 0.3
        
        # Constructive interference suggests growth
        if interference['balance'] == 'constructive':
            evolution_potential += 0.2
        
        # Standing waves suggest stability
        if vibration['standing_waves'] > 3:
            evolution_potential += 0.2
        
        # Determine next phase
        if evolution_potential > 0.7:
            next_phase = "breakthrough_imminent"
            suggestion = "System ready for major evolution"
        elif evolution_potential > 0.5:
            next_phase = "convergence_building"
            suggestion = "Continue current patterns"
        elif evolution_potential > 0.3:
            next_phase = "pattern_formation"
            suggestion = "Focus on pattern reinforcement"
        else:
            next_phase = "exploration"
            suggestion = "Increase variety of actions"
        
        return {
            'evolution_potential': round(evolution_potential, 3),
            'next_phase': next_phase,
            'suggestion': suggestion,
            'key_indicators': {
                'vibration': vibration['vibration'],
                'convergence': convergence['convergent_groups'],
                'interference': interference['balance'],
                'stability': vibration['stability']
            }
        }
    
    async def _store_pattern(self, pattern: ResonancePattern):
        """Store pattern in database."""
        if not self.pool:
            return
        
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO evolution.resonance_field (
                    resonance_id, pattern_signature, pattern_type,
                    source_event_id, source_intent_id, source_actor,
                    frequency, amplitude, wavelength, phase,
                    harmonics, harmonic_convergence, interference_pattern,
                    affected_agents, affected_intents, ripple_radius,
                    standing_wave, persistence_cycles, decay_rate,
                    detected_at, last_observed, observation_count,
                    field_contribution
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                         $11, $12, $13, $14, $15, $16, $17, $18, $19,
                         $20, $21, $22, $23)
            """,
                pattern.resonance_id, pattern.pattern_signature, pattern.pattern_type.value,
                pattern.source_event_id, pattern.source_intent_id, pattern.source_actor,
                pattern.frequency, pattern.amplitude, pattern.wavelength, pattern.phase,
                pattern.harmonics, pattern.harmonic_convergence,
                pattern.interference_pattern.value if pattern.interference_pattern else None,
                pattern.affected_agents, pattern.affected_intents, pattern.ripple_radius,
                pattern.standing_wave, pattern.persistence_cycles, pattern.decay_rate,
                pattern.detected_at, pattern.last_observed, pattern.observation_count,
                pattern.field_contribution
            )
    
    async def close(self):
        """Close database connections."""
        if self.pool:
            await self.pool.close()


# Demo and testing
async def demo_resonance_analyzer():
    """Demonstrate the Resonance Analyzer."""
    
    analyzer = ResonanceAnalyzer()
    await analyzer.initialize()
    
    print("\n🌊 Resonance Analyzer Demo\n" + "="*50)
    
    # Simulate various events
    events = [
        {'event_type': 'planning', 'actor': 'planner', 'success': True, 'coherence': 0.8},
        {'event_type': 'implementation', 'actor': 'developer', 'success': True, 'impact': 'high'},
        {'event_type': 'testing', 'actor': 'tester', 'success': False, 'error': True},
        {'event_type': 'planning', 'actor': 'planner', 'success': True, 'coherence': 0.9},
        {'event_type': 'optimization', 'actor': 'optimizer', 'success': True, 'complexity': 1.5},
        {'event_type': 'planning', 'actor': 'planner', 'success': True, 'coherence': 0.85},
        {'event_type': 'innovation', 'actor': 'architect', 'is_new': True, 'breakthrough': True}
    ]
    
    print("\n1. Detecting patterns from events...")
    for event in events:
        pattern = await analyzer.detect_pattern(event)
        symbol = "🌊" if pattern.standing_wave else "〰️"
        print(f"  {symbol} {event['event_type']}: freq={pattern.frequency:.1f}Hz, "
              f"amp={pattern.amplitude:.2f}, type={pattern.pattern_type.value}")
    
    print("\n2. Detecting standing waves...")
    standing = await analyzer.detect_standing_waves()
    for wave in standing:
        print(f"  🌊 Standing wave: {wave.pattern_signature[:8]}... "
              f"(cycles={wave.persistence_cycles})")
    
    print("\n3. Measuring system vibration...")
    vibration = await analyzer.measure_system_vibration()
    print(f"  Frequency: {vibration['vibration']}Hz ({vibration['dominant_band']} band)")
    print(f"  Energy: {vibration['energy']}")
    print(f"  Stability: {vibration['stability']}")
    
    print("\n4. Finding harmonic convergence...")
    convergence = await analyzer.find_harmonic_convergence()
    print(f"  Convergent groups: {convergence['convergent_groups']}")
    if convergence['groups']:
        print(f"  Top group convergence: {convergence['groups'][0]['avg_convergence']:.2f}")
    
    print("\n5. Analyzing interference...")
    interference = await analyzer.analyze_interference_patterns()
    print(f"  Constructive: {interference['constructive']}")
    print(f"  Destructive: {interference['destructive']}")
    print(f"  Balance: {interference['balance']}")
    
    print("\n6. Predicting evolution...")
    prediction = await analyzer.predict_evolution()
    print(f"  Evolution potential: {prediction['evolution_potential']}")
    print(f"  Next phase: {prediction['next_phase']}")
    print(f"  Suggestion: {prediction['suggestion']}")
    
    print("\n" + "="*50)
    print("✅ Resonance Analyzer ready for pattern detection!")


if __name__ == "__main__":
    print("\n🌊 Resonance Analyzer - Pattern Detection Layer\n" + "="*50)
    print("This module detects and analyzes patterns in the system.")
    print("\nKey features:")
    print("- Standing wave detection")
    print("- Harmonic convergence analysis")
    print("- Interference pattern detection")
    print("- System vibration measurement")
    print("- Evolution prediction")
    print("="*50)
    
    # Run demo
    asyncio.run(demo_resonance_analyzer())