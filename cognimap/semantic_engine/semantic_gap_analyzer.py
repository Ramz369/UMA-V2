#!/usr/bin/env python3
"""
Semantic Gap Analyzer - Identifies architectural gaps from semantic data alone
No code analysis needed - works purely with semantic fingerprints and relationships
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
import hashlib


class SemanticGapAnalyzer:
    """Analyzes gaps using only semantic database - no code needed"""
    
    def __init__(self, semantic_path: str = "reports/cognimap/semantic"):
        self.semantic_path = Path(semantic_path)
        self.symbol_graph = {}
        self.connections = {}
        self.patterns = {}
        self.load_semantic_data()
    
    def load_semantic_data(self):
        """Load semantic database files"""
        # Load symbol graph
        symbol_path = self.semantic_path / "symbol_graph.json"
        if symbol_path.exists():
            with open(symbol_path, 'r') as f:
                self.symbol_graph = json.load(f)
        
        # Load connections
        conn_path = self.semantic_path / "semantic_connections.json"
        if conn_path.exists():
            with open(conn_path, 'r') as f:
                self.connections = json.load(f)
        
        # Load patterns
        pattern_path = self.semantic_path / "architectural_patterns.json"
        if pattern_path.exists():
            with open(pattern_path, 'r') as f:
                self.patterns = json.load(f)
    
    def analyze_all_gaps(self) -> Dict[str, Any]:
        """Comprehensive gap analysis from semantic data"""
        return {
            'orphaned_symbols': self.find_orphaned_symbols(),
            'missing_tests': self.find_missing_tests(),
            'circular_dependencies': self.find_circular_dependencies(),
            'highly_coupled': self.find_highly_coupled_components(),
            'architectural_imbalance': self.find_architectural_imbalance(),
            'missing_connections': self.find_missing_logical_connections(),
            'pattern_violations': self.find_pattern_violations(),
            'documentation_gaps': self.find_documentation_gaps()
        }
    
    def find_orphaned_symbols(self) -> List[Dict]:
        """Find symbols with no connections"""
        orphans = []
        
        for symbol_id, symbol_data in self.symbol_graph.items():
            file = symbol_data.get('file', '')
            refs = symbol_data.get('references', [])
            
            # Check if symbol has no references except itself
            if len(refs) <= 1 and file in refs:
                orphans.append({
                    'symbol': symbol_id,
                    'file': file,
                    'type': symbol_data.get('type', 'unknown'),
                    'severity': 'high' if 'class' in symbol_data.get('type', '') else 'medium'
                })
        
        return orphans
    
    def find_missing_tests(self) -> List[Dict]:
        """Find components without test coverage"""
        missing = []
        
        # Get all files from connections
        all_files = set(self.connections.keys())
        test_files = {f for f in all_files if 'test' in f.lower()}
        source_files = all_files - test_files
        
        for source_file in source_files:
            # Skip non-code files
            if not source_file.endswith('.py'):
                continue
            
            # Check if there's a corresponding test file
            base_name = Path(source_file).stem
            has_test = any(
                f"test_{base_name}" in test_file or 
                f"{base_name}_test" in test_file
                for test_file in test_files
            )
            
            if not has_test:
                # Count symbols in file to determine importance
                symbol_count = sum(
                    1 for s in self.symbol_graph.values() 
                    if s.get('file') == source_file
                )
                
                missing.append({
                    'file': source_file,
                    'symbols': symbol_count,
                    'severity': 'high' if symbol_count > 5 else 'medium',
                    'suggestion': f"Create test_{base_name}.py"
                })
        
        return missing
    
    def find_circular_dependencies(self) -> List[Dict]:
        """Detect circular import patterns"""
        circles = []
        visited = set()
        
        def find_cycle(file, path, connections):
            if file in path:
                # Found a cycle
                cycle_start = path.index(file)
                cycle = path[cycle_start:] + [file]
                cycle_key = tuple(sorted(cycle))
                
                if cycle_key not in visited:
                    visited.add(cycle_key)
                    return cycle
                return None
            
            if file not in connections:
                return None
            
            for target in connections[file].get('outgoing', []):
                if target != file:  # Skip self-references
                    result = find_cycle(target, path + [file], connections)
                    if result:
                        return result
            
            return None
        
        for file in self.connections:
            cycle = find_cycle(file, [], self.connections)
            if cycle and len(cycle) > 2:  # Only report non-trivial cycles
                circles.append({
                    'cycle': cycle,
                    'length': len(cycle) - 1,
                    'severity': 'critical' if len(cycle) > 4 else 'high'
                })
        
        return circles
    
    def find_highly_coupled_components(self) -> List[Dict]:
        """Find components with too many dependencies"""
        coupled = []
        
        for file, conn_data in self.connections.items():
            incoming = len(conn_data.get('incoming', []))
            outgoing = len(conn_data.get('outgoing', []))
            total = incoming + outgoing
            
            # High coupling threshold
            if total > 15:
                coupled.append({
                    'file': file,
                    'incoming': incoming,
                    'outgoing': outgoing,
                    'total_connections': total,
                    'severity': 'critical' if total > 20 else 'high',
                    'suggestion': 'Consider breaking into smaller modules'
                })
        
        return sorted(coupled, key=lambda x: x['total_connections'], reverse=True)
    
    def find_architectural_imbalance(self) -> Dict:
        """Analyze distribution of components across layers"""
        layers = defaultdict(list)
        
        # Categorize files by architectural layer
        for file in self.connections.keys():
            if 'semantic' in file:
                layers['semantic'].append(file)
            elif 'graph' in file:
                layers['graph'].append(file)
            elif 'visualizer' in file or 'visual' in file:
                layers['visualization'].append(file)
            elif 'core' in file:
                layers['core'].append(file)
            elif 'collector' in file:
                layers['collector'].append(file)
            elif 'server' in file or 'ai_server' in file:
                layers['server'].append(file)
            else:
                layers['other'].append(file)
        
        # Analyze balance
        total_files = sum(len(files) for files in layers.values())
        imbalances = []
        
        for layer, files in layers.items():
            percentage = (len(files) / total_files) * 100 if total_files > 0 else 0
            
            if percentage > 40:  # Layer too heavy
                imbalances.append({
                    'layer': layer,
                    'file_count': len(files),
                    'percentage': percentage,
                    'issue': 'Layer too heavy',
                    'suggestion': f'Consider splitting {layer} into sub-modules'
                })
            elif percentage < 5 and len(files) > 0:  # Layer too light
                imbalances.append({
                    'layer': layer,
                    'file_count': len(files),
                    'percentage': percentage,
                    'issue': 'Layer too light',
                    'suggestion': f'Consider merging {layer} with related layer'
                })
        
        return {
            'distribution': {k: len(v) for k, v in layers.items()},
            'imbalances': imbalances,
            'total_files': total_files
        }
    
    def find_missing_logical_connections(self) -> List[Dict]:
        """Find components that should be connected but aren't"""
        missing = []
        
        # Semantic engine should connect to graph engine
        semantic_files = [f for f in self.connections if 'semantic' in f]
        graph_files = [f for f in self.connections if 'graph' in f]
        
        for sem_file in semantic_files:
            sem_connections = self.connections.get(sem_file, {})
            connected_to_graph = any(
                g in sem_connections.get('outgoing', []) or 
                g in sem_connections.get('incoming', [])
                for g in graph_files
            )
            
            if not connected_to_graph and 'test' not in sem_file:
                missing.append({
                    'from': sem_file,
                    'to_layer': 'graph',
                    'type': 'missing_layer_connection',
                    'suggestion': 'Semantic engine should connect to graph engine'
                })
        
        # AI server should connect to semantic engine
        if 'ai_server.py' in self.connections:
            ai_connections = self.connections['ai_server.py']
            if not any('semantic' in f for f in ai_connections.get('outgoing', [])):
                missing.append({
                    'from': 'ai_server.py',
                    'to_layer': 'semantic',
                    'type': 'missing_integration',
                    'suggestion': 'AI server should use semantic engine'
                })
        
        return missing
    
    def find_pattern_violations(self) -> List[Dict]:
        """Find violations of architectural patterns"""
        violations = []
        
        # Check for direct database access from visualization
        viz_files = [f for f in self.connections if 'visualizer' in f]
        for viz_file in viz_files:
            connections = self.connections.get(viz_file, {})
            
            # Visualization shouldn't directly access core
            if any('core' in f for f in connections.get('outgoing', [])):
                violations.append({
                    'file': viz_file,
                    'pattern': 'layer_violation',
                    'issue': 'Visualization directly accessing core',
                    'suggestion': 'Use graph engine as intermediary'
                })
        
        return violations
    
    def find_documentation_gaps(self) -> List[Dict]:
        """Find components lacking documentation connections"""
        doc_gaps = []
        
        # Check for README connections
        has_readme = 'README.md' in self.connections
        
        if not has_readme:
            doc_gaps.append({
                'type': 'missing_readme',
                'severity': 'high',
                'suggestion': 'Add README.md with project overview'
            })
        
        # Check for architecture docs
        doc_files = [f for f in self.connections if '.md' in f.lower()]
        
        if len(doc_files) < 3:
            doc_gaps.append({
                'type': 'insufficient_documentation',
                'current_docs': len(doc_files),
                'suggestion': 'Add architecture and API documentation'
            })
        
        return doc_gaps
    
    def create_deepseek_prompt(self, gaps: Dict[str, Any]) -> str:
        """Create focused prompt for DeepSeek with semantic gaps only"""
        prompt = f"""Analyze these architectural gaps found in CogniMap's semantic database:

## Semantic Database Overview
- Total Symbols: {len(self.symbol_graph)}
- Total Files: {len(self.connections)}
- Architectural Layers: {', '.join(self.find_architectural_imbalance()['distribution'].keys())}

## Identified Gaps

### 1. Orphaned Components ({len(gaps['orphaned_symbols'])} found)
{json.dumps(gaps['orphaned_symbols'][:5], indent=2) if gaps['orphaned_symbols'] else 'None found'}

### 2. Missing Test Coverage ({len(gaps['missing_tests'])} files)
{json.dumps(gaps['missing_tests'][:5], indent=2) if gaps['missing_tests'] else 'All files have tests'}

### 3. Circular Dependencies ({len(gaps['circular_dependencies'])} cycles)
{json.dumps(gaps['circular_dependencies'][:3], indent=2) if gaps['circular_dependencies'] else 'No cycles detected'}

### 4. Highly Coupled Components ({len(gaps['highly_coupled'])} found)
{json.dumps(gaps['highly_coupled'][:3], indent=2) if gaps['highly_coupled'] else 'No high coupling'}

### 5. Architectural Imbalance
{json.dumps(gaps['architectural_imbalance'], indent=2)}

### 6. Missing Logical Connections ({len(gaps['missing_connections'])} found)
{json.dumps(gaps['missing_connections'], indent=2) if gaps['missing_connections'] else 'All layers connected'}

Based on this semantic analysis, provide:
1. Priority ranking of issues to fix
2. Specific refactoring suggestions
3. New components or abstractions needed
4. Architecture improvements for better separation of concerns
5. Testing strategy to improve coverage

Focus on architectural improvements, not implementation details."""
        
        return prompt
    
    def analyze_for_deepseek(self) -> Dict[str, Any]:
        """Prepare semantic gap analysis for DeepSeek"""
        gaps = self.analyze_all_gaps()
        prompt = self.create_deepseek_prompt(gaps)
        
        # Calculate metrics
        total_issues = sum(
            len(v) if isinstance(v, list) else 
            len(v.get('imbalances', [])) if isinstance(v, dict) else 0
            for v in gaps.values()
        )
        
        return {
            'gaps': gaps,
            'prompt': prompt,
            'metrics': {
                'total_issues': total_issues,
                'critical_issues': len(gaps.get('circular_dependencies', [])),
                'high_priority': len(gaps.get('highly_coupled', [])) + len(gaps.get('orphaned_symbols', [])),
                'test_coverage_gaps': len(gaps.get('missing_tests', [])),
                'prompt_tokens': len(prompt) // 4  # Rough estimate
            }
        }


if __name__ == "__main__":
    # Test the semantic gap analyzer
    analyzer = SemanticGapAnalyzer()
    result = analyzer.analyze_for_deepseek()
    
    print("Semantic Gap Analysis")
    print("=" * 50)
    print(f"Total Issues Found: {result['metrics']['total_issues']}")
    print(f"Critical Issues: {result['metrics']['critical_issues']}")
    print(f"High Priority: {result['metrics']['high_priority']}")
    print(f"Test Coverage Gaps: {result['metrics']['test_coverage_gaps']}")
    print(f"Prompt Size: ~{result['metrics']['prompt_tokens']} tokens")
    
    # Save analysis
    output_path = Path("reports/cognimap/semantic/semantic_gap_analysis.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result['gaps'], f, indent=2)
    
    print(f"\nDetailed analysis saved to: {output_path}")
    print("\nSample prompt for DeepSeek (first 1000 chars):")
    print(result['prompt'][:1000] + "...")