"""
Graph Visualizer - Create visual representations of the architecture.
"""

from typing import Dict, List, Any
from pathlib import Path


class GraphVisualizer:
    """Creates visual representations of the architecture graph."""
    
    def __init__(self, graph: Dict[str, Any]):
        self.graph = graph
        self.nodes = {n['filepath']: n for n in graph['nodes']}
        self.edges = graph['edges']
        
    def create_text_visualization(self) -> str:
        """Create a text-based visualization of the architecture."""
        output = []
        output.append("=" * 80)
        output.append("🏗️  COGPLAN ARCHITECTURE MAP")
        output.append("=" * 80)
        output.append("")
        
        # Group nodes by type
        type_groups = {}
        for filepath, node in self.nodes.items():
            node_type = node['type']
            if node_type not in type_groups:
                type_groups[node_type] = []
            type_groups[node_type].append(node)
        
        # Display each component type
        type_icons = {
            'agent': '🤖',
            'tool': '🔧',
            'service': '⚙️',
            'model': '📊',
            'test': '🧪',
            'configuration': '⚙️',
            'protocol': '📡',
            'component': '📦'
        }
        
        for comp_type, nodes in sorted(type_groups.items()):
            icon = type_icons.get(comp_type, '📄')
            output.append(f"\n{icon} {comp_type.upper()}S ({len(nodes)})")
            output.append("-" * 40)
            
            for node in sorted(nodes, key=lambda x: x['filepath']):
                name = Path(node['filepath']).stem
                filepath = node['filepath']
                tags = node.get('semantic_tags', [])
                
                # Count connections
                imports = len([e for e in self.edges if e['source'] == filepath and e['type'] == 'imports'])
                imported_by = len([e for e in self.edges if e['target'] == filepath and e['type'] == 'imports'])
                
                output.append(f"  • {name}")
                output.append(f"    📁 {filepath}")
                if tags:
                    output.append(f"    🏷️  {', '.join(tags[:5])}")
                if imports > 0 or imported_by > 0:
                    output.append(f"    🔗 imports: {imports}, imported by: {imported_by}")
        
        # Add statistics
        stats = self.graph.get('statistics', {})
        output.append("\n" + "=" * 80)
        output.append("📊 STATISTICS")
        output.append("=" * 80)
        output.append(f"  Total Nodes: {self.graph['metadata']['node_count']}")
        output.append(f"  Total Edges: {self.graph['metadata']['edge_count']}")
        output.append(f"  Languages: {', '.join(self.graph['metadata']['languages'])}")
        output.append(f"  Connectivity: {stats.get('connectivity', 0):.1%}")
        
        # Most connected components
        if stats.get('most_imported'):
            output.append("\n  🎯 Most Imported Components:")
            for filepath, count in stats['most_imported']:
                name = Path(filepath).stem
                output.append(f"    • {name} ({count} imports)")
        
        if stats.get('most_importing'):
            output.append("\n  📦 Most Dependent Components:")
            for filepath, count in stats['most_importing']:
                name = Path(filepath).stem
                output.append(f"    • {name} ({count} dependencies)")
        
        if stats.get('isolated_nodes'):
            output.append(f"\n  ⚠️  Isolated Components: {len(stats['isolated_nodes'])}")
            for filepath in stats['isolated_nodes'][:5]:
                name = Path(filepath).stem
                output.append(f"    • {name}")
        
        return "\n".join(output)
    
    def create_dependency_tree(self, root_file: str = None) -> str:
        """Create a dependency tree visualization."""
        output = []
        output.append("🌳 DEPENDENCY TREE")
        output.append("=" * 60)
        
        if root_file:
            # Show tree from specific file
            self._add_tree_node(output, root_file, "", set())
        else:
            # Show trees for main components
            agents = [f for f, n in self.nodes.items() if n['type'] == 'agent']
            for agent in agents[:3]:  # Limit to avoid huge output
                output.append(f"\n📍 {Path(agent).stem}")
                self._add_tree_node(output, agent, "  ", set())
        
        return "\n".join(output)
    
    def _add_tree_node(self, output: List[str], filepath: str, prefix: str, visited: set):
        """Recursively add nodes to dependency tree."""
        if filepath in visited:
            output.append(f"{prefix}↻ {Path(filepath).stem} (circular)")
            return
        
        visited.add(filepath)
        
        # Find dependencies
        deps = [e['target'] for e in self.edges 
                if e['source'] == filepath and e['type'] == 'imports']
        
        for i, dep in enumerate(deps[:5]):  # Limit depth
            is_last = i == len(deps) - 1
            branch = "└── " if is_last else "├── "
            extension = "    " if is_last else "│   "
            
            if dep in self.nodes:
                node = self.nodes[dep]
                name = Path(dep).stem
                node_type = node['type']
                output.append(f"{prefix}{branch}{name} ({node_type})")
                
                # Recurse if not too deep
                if len(prefix) < 12:  # Limit depth
                    self._add_tree_node(output, dep, prefix + extension, visited.copy())
    
    def create_mermaid_diagram(self) -> str:
        """Create a Mermaid diagram for better visualization."""
        output = []
        output.append("```mermaid")
        output.append("graph TD")
        output.append("    %% COGPLAN Architecture")
        
        # Add nodes grouped by type
        type_groups = {}
        for filepath, node in self.nodes.items():
            node_type = node['type']
            if node_type not in type_groups:
                type_groups[node_type] = []
            type_groups[node_type].append(node)
        
        # Create subgraphs for each type
        for comp_type, nodes in type_groups.items():
            if len(nodes) > 0:
                output.append(f"\n    subgraph {comp_type.upper()}")
                for node in nodes[:10]:  # Limit for readability
                    node_id = node['filepath'].replace('/', '_').replace('.', '_')
                    name = Path(node['filepath']).stem
                    output.append(f"        {node_id}[{name}]")
                output.append("    end")
        
        # Add edges (limit for readability)
        output.append("\n    %% Relationships")
        edge_count = 0
        for edge in self.edges:
            if edge_count >= 30:  # Limit edges for readability
                break
            source_id = edge['source'].replace('/', '_').replace('.', '_')
            target_id = edge['target'].replace('/', '_').replace('.', '_')
            
            if edge['source'] in self.nodes and edge['target'] in self.nodes:
                rel_type = edge['type']
                if rel_type == 'imports':
                    output.append(f"    {source_id} --> {target_id}")
                elif rel_type == 'semantic_related':
                    output.append(f"    {source_id} -.-> {target_id}")
                elif rel_type == 'uses':
                    output.append(f"    {source_id} ==> {target_id}")
                edge_count += 1
        
        output.append("```")
        return "\n".join(output)