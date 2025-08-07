"""
Graph Analyzer - Analyze architecture patterns and issues.
"""

from typing import Dict, List, Any, Set, Tuple
from pathlib import Path


class GraphAnalyzer:
    """Analyzes the architecture graph for patterns and issues."""
    
    def __init__(self, graph: Dict[str, Any]):
        self.graph = graph
        self.nodes = {n['filepath']: n for n in graph['nodes']}
        self.edges = graph['edges']
        
    def analyze(self) -> Dict[str, Any]:
        """Perform complete analysis of the architecture."""
        return {
            'circular_dependencies': self._find_circular_dependencies(),
            'complexity_analysis': self._analyze_complexity(),
            'cohesion_analysis': self._analyze_cohesion(),
            'coupling_analysis': self._analyze_coupling(),
            'architectural_issues': self._find_architectural_issues(),
            'recommendations': self._generate_recommendations()
        }
    
    def _find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the graph."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            # Get neighbors
            neighbors = [e['target'] for e in self.edges 
                        if e['source'] == node and e['type'] == 'imports']
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if len(cycle) > 2 and cycle not in cycles:
                        cycles.append(cycle)
            
            rec_stack.remove(node)
        
        # Check each node
        for node in self.nodes:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _analyze_complexity(self) -> Dict[str, Any]:
        """Analyze complexity metrics."""
        # Calculate cyclomatic complexity proxy (number of decision points)
        complexity_scores = {}
        
        for filepath, node in self.nodes.items():
            # Base complexity from imports and exports
            imports = len([e for e in self.edges if e['source'] == filepath])
            exports = len(node.get('exports', []))
            
            # Factor in semantic tags (more tags = more complex)
            tag_complexity = len(node.get('semantic_tags', []))
            
            # Calculate score
            complexity = imports + exports + tag_complexity
            complexity_scores[filepath] = complexity
        
        # Find most complex files
        most_complex = sorted(complexity_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'most_complex_files': most_complex,
            'average_complexity': sum(complexity_scores.values()) / len(complexity_scores) if complexity_scores else 0,
            'complexity_distribution': self._calculate_distribution(complexity_scores.values())
        }
    
    def _analyze_cohesion(self) -> Dict[str, Any]:
        """Analyze module cohesion."""
        # Group files by directory
        module_cohesion = {}
        
        for filepath in self.nodes:
            module = str(Path(filepath).parent)
            if module not in module_cohesion:
                module_cohesion[module] = {
                    'files': [],
                    'internal_connections': 0,
                    'external_connections': 0
                }
            module_cohesion[module]['files'].append(filepath)
        
        # Calculate internal vs external connections
        for edge in self.edges:
            if edge['type'] == 'imports':
                source_module = str(Path(edge['source']).parent)
                target_module = str(Path(edge['target']).parent)
                
                if source_module in module_cohesion:
                    if source_module == target_module:
                        module_cohesion[source_module]['internal_connections'] += 1
                    else:
                        module_cohesion[source_module]['external_connections'] += 1
        
        # Calculate cohesion scores
        cohesion_scores = {}
        for module, data in module_cohesion.items():
            total = data['internal_connections'] + data['external_connections']
            if total > 0:
                cohesion_scores[module] = data['internal_connections'] / total
            else:
                cohesion_scores[module] = 0
        
        return {
            'module_cohesion': cohesion_scores,
            'average_cohesion': sum(cohesion_scores.values()) / len(cohesion_scores) if cohesion_scores else 0,
            'low_cohesion_modules': [m for m, s in cohesion_scores.items() if s < 0.3]
        }
    
    def _analyze_coupling(self) -> Dict[str, Any]:
        """Analyze coupling between modules."""
        # Calculate afferent and efferent coupling
        afferent = {}  # Incoming dependencies
        efferent = {}  # Outgoing dependencies
        
        for edge in self.edges:
            if edge['type'] == 'imports':
                source = edge['source']
                target = edge['target']
                
                efferent[source] = efferent.get(source, 0) + 1
                afferent[target] = afferent.get(target, 0) + 1
        
        # Calculate instability (I = Ce / (Ca + Ce))
        instability = {}
        for node in self.nodes:
            ca = afferent.get(node, 0)
            ce = efferent.get(node, 0)
            if ca + ce > 0:
                instability[node] = ce / (ca + ce)
            else:
                instability[node] = 0
        
        # Find highly coupled components
        highly_coupled = [
            (node, afferent.get(node, 0) + efferent.get(node, 0))
            for node in self.nodes
        ]
        highly_coupled.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'highly_coupled_components': highly_coupled[:10],
            'average_coupling': sum(afferent.values()) + sum(efferent.values()) / (2 * len(self.nodes)) if self.nodes else 0,
            'instability_scores': instability,
            'stable_components': [n for n, i in instability.items() if i < 0.3],
            'unstable_components': [n for n, i in instability.items() if i > 0.7]
        }
    
    def _find_architectural_issues(self) -> List[Dict[str, Any]]:
        """Find potential architectural issues."""
        issues = []
        
        # Check for circular dependencies
        cycles = self._find_circular_dependencies()
        if cycles:
            for cycle in cycles:
                issues.append({
                    'type': 'circular_dependency',
                    'severity': 'high',
                    'components': cycle,
                    'description': f"Circular dependency detected: {' -> '.join(Path(f).stem for f in cycle)}"
                })
        
        # Check for god objects (highly connected components)
        coupling = self._analyze_coupling()
        for component, coupling_score in coupling['highly_coupled_components'][:3]:
            if coupling_score > 20:
                issues.append({
                    'type': 'god_object',
                    'severity': 'medium',
                    'component': component,
                    'description': f"{Path(component).stem} has {coupling_score} connections (possible god object)"
                })
        
        # Check for isolated components
        stats = self.graph.get('statistics', {})
        isolated = stats.get('isolated_nodes', [])
        if len(isolated) > 5:
            issues.append({
                'type': 'isolated_components',
                'severity': 'low',
                'count': len(isolated),
                'description': f"{len(isolated)} components have no connections"
            })
        
        # Check for missing tests
        test_files = [f for f, n in self.nodes.items() if n['type'] == 'test']
        src_files = [f for f, n in self.nodes.items() if n['type'] in ('agent', 'service', 'tool')]
        if len(test_files) < len(src_files) * 0.5:
            issues.append({
                'type': 'insufficient_tests',
                'severity': 'medium',
                'test_ratio': len(test_files) / len(src_files) if src_files else 0,
                'description': f"Only {len(test_files)} test files for {len(src_files)} source files"
            })
        
        return issues
    
    def _generate_recommendations(self) -> List[str]:
        """Generate architectural recommendations."""
        recommendations = []
        
        issues = self._find_architectural_issues()
        
        # Recommendations based on issues
        for issue in issues:
            if issue['type'] == 'circular_dependency':
                recommendations.append(
                    f"🔄 Break circular dependency in {issue['components'][0]} by introducing an interface or event system"
                )
            elif issue['type'] == 'god_object':
                recommendations.append(
                    f"🎯 Refactor {Path(issue['component']).stem} - split responsibilities into smaller components"
                )
            elif issue['type'] == 'isolated_components':
                recommendations.append(
                    f"🔗 Review {issue['count']} isolated components - they may be unused or need integration"
                )
            elif issue['type'] == 'insufficient_tests':
                recommendations.append(
                    f"🧪 Increase test coverage - current ratio is {issue['test_ratio']:.1%}"
                )
        
        # General recommendations
        cohesion = self._analyze_cohesion()
        if cohesion['average_cohesion'] < 0.5:
            recommendations.append(
                "📦 Improve module cohesion - consider reorganizing related components"
            )
        
        complexity = self._analyze_complexity()
        if complexity['average_complexity'] > 15:
            recommendations.append(
                "🔧 Reduce overall complexity - consider extracting common functionality"
            )
        
        return recommendations
    
    def _calculate_distribution(self, values: List[float]) -> Dict[str, int]:
        """Calculate distribution of values."""
        if not values:
            return {}
        
        distribution = {
            'low': 0,
            'medium': 0,
            'high': 0
        }
        
        avg = sum(values) / len(values)
        
        for value in values:
            if value < avg * 0.5:
                distribution['low'] += 1
            elif value < avg * 1.5:
                distribution['medium'] += 1
            else:
                distribution['high'] += 1
        
        return distribution