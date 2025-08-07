"""
Graph Builder - Constructs architecture graph from fingerprints.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
import ast


class GraphNode:
    """Represents a node in the architecture graph."""
    
    def __init__(self, filepath: str, fingerprint: Dict[str, Any]):
        self.id = fingerprint.get('id', filepath)
        self.filepath = filepath
        self.fingerprint = fingerprint
        self.name = Path(filepath).stem
        self.type = fingerprint.get('type', 'unknown')
        self.language = fingerprint.get('language', 'unknown')
        self.semantic_tags = fingerprint.get('semantic_tags', [])
        self.imports = set()
        self.exports = set()
        self.calls = set()
        self.dependencies = set()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary."""
        return {
            'id': self.id,
            'filepath': self.filepath,
            'name': self.name,
            'type': self.type,
            'language': self.language,
            'semantic_tags': self.semantic_tags,
            'imports': list(self.imports),
            'exports': list(self.exports),
            'calls': list(self.calls),
            'dependencies': list(self.dependencies),
            'fingerprint': self.fingerprint
        }


class GraphEdge:
    """Represents an edge/relationship in the graph."""
    
    def __init__(self, source: str, target: str, relationship_type: str, metadata: Dict = None):
        self.source = source
        self.target = target
        self.type = relationship_type
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary."""
        return {
            'source': self.source,
            'target': self.target,
            'type': self.type,
            'metadata': self.metadata
        }


class GraphBuilder:
    """Builds architecture graph from CogniMap fingerprints."""
    
    def __init__(self, project_path: str = '.'):
        self.project_path = Path(project_path)
        self.nodes = {}  # filepath -> GraphNode
        self.edges = []  # List of GraphEdge
        self.fingerprints = {}  # filepath -> fingerprint data
        
    def build(self) -> Dict[str, Any]:
        """Build the complete architecture graph."""
        print("🔨 Building architecture graph...")
        
        # Step 1: Collect all fingerprints
        self._collect_fingerprints()
        print(f"  ✓ Collected {len(self.fingerprints)} fingerprints")
        
        # Step 2: Create nodes
        self._create_nodes()
        print(f"  ✓ Created {len(self.nodes)} nodes")
        
        # Step 3: Analyze relationships
        self._analyze_relationships()
        print(f"  ✓ Found {len(self.edges)} relationships")
        
        # Step 4: Build graph structure
        graph = self._build_graph_structure()
        print("  ✓ Graph built successfully!")
        
        return graph
    
    def _collect_fingerprints(self):
        """Collect all fingerprints from Python files."""
        for filepath in self.project_path.rglob('*.py'):
            if any(skip in str(filepath) for skip in ['__pycache__', '.venv', 'node_modules']):
                continue
            
            try:
                content = filepath.read_text(encoding='utf-8')
                fingerprint = self._extract_fingerprint(content)
                if fingerprint:
                    rel_path = str(filepath.relative_to(self.project_path))
                    self.fingerprints[rel_path] = fingerprint
            except:
                continue
    
    def _extract_fingerprint(self, content: str) -> Dict[str, Any]:
        """Extract fingerprint from file content."""
        pattern = r'@cognimap:fingerprint\n(.*?)@end:cognimap'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            fingerprint_text = match.group(1)
            fingerprint = {}
            
            for line in fingerprint_text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Parse different value types
                    if value.startswith('[') and value.endswith(']'):
                        # Parse list
                        value = [v.strip() for v in value[1:-1].split(',') if v.strip()]
                    elif value in ('None', 'null'):
                        value = None
                    
                    fingerprint[key] = value
            
            return fingerprint
        return None
    
    def _create_nodes(self):
        """Create graph nodes from fingerprints."""
        for filepath, fingerprint in self.fingerprints.items():
            node = GraphNode(filepath, fingerprint)
            
            # Analyze file content for additional metadata
            full_path = self.project_path / filepath
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding='utf-8')
                    self._analyze_file_content(node, content)
                except:
                    pass
            
            self.nodes[filepath] = node
    
    def _analyze_file_content(self, node: GraphNode, content: str):
        """Analyze file content to extract imports, exports, etc."""
        if node.language == 'python':
            self._analyze_python_content(node, content)
    
    def _analyze_python_content(self, node: GraphNode, content: str):
        """Analyze Python file content."""
        # Extract imports
        import_pattern = r'^(?:from\s+([\w\.]+)\s+)?import\s+([\w\s,*]+)'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module = match.group(1) or match.group(2)
            if module:
                # Convert relative imports to absolute based on file location
                if module.startswith('.'):
                    module = self._resolve_relative_import(node.filepath, module)
                node.imports.add(module)
        
        # Extract class definitions (exports)
        class_pattern = r'^class\s+(\w+)'
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            node.exports.add(match.group(1))
        
        # Extract function definitions (exports)
        func_pattern = r'^def\s+(\w+)'
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            node.exports.add(match.group(1))
    
    def _resolve_relative_import(self, filepath: str, module: str) -> str:
        """Resolve relative import to absolute path."""
        file_parts = Path(filepath).parts[:-1]  # Remove filename
        
        if module.startswith('..'):
            # Go up directories
            levels = module.count('..')
            if levels < len(file_parts):
                base = file_parts[:-levels]
                rest = module[levels * 2:].lstrip('.')
                if rest:
                    return '.'.join(base) + '.' + rest
                return '.'.join(base)
        elif module.startswith('.'):
            # Same directory
            rest = module[1:].lstrip('.')
            if rest:
                return '.'.join(file_parts) + '.' + rest
            return '.'.join(file_parts)
        
        return module
    
    def _analyze_relationships(self):
        """Analyze relationships between nodes."""
        # Create import relationships
        for filepath, node in self.nodes.items():
            for imp in node.imports:
                # Find target node
                target_file = self._find_file_for_module(imp)
                if target_file and target_file in self.nodes:
                    edge = GraphEdge(
                        source=filepath,
                        target=target_file,
                        relationship_type='imports',
                        metadata={'module': imp}
                    )
                    self.edges.append(edge)
                    node.dependencies.add(target_file)
        
        # Create semantic relationships
        self._create_semantic_relationships()
        
        # Create type-based relationships
        self._create_type_relationships()
    
    def _find_file_for_module(self, module: str) -> str:
        """Find the file path for a given module."""
        # Convert module to potential file paths
        module_parts = module.split('.')
        
        # Try different combinations
        potential_paths = [
            '/'.join(module_parts) + '.py',
            '/'.join(module_parts) + '/__init__.py',
        ]
        
        for path in potential_paths:
            if path in self.nodes:
                return path
            # Try without leading directories
            for i in range(1, len(module_parts)):
                subpath = '/'.join(module_parts[i:]) + '.py'
                if subpath in self.nodes:
                    return subpath
        
        return None
    
    def _create_semantic_relationships(self):
        """Create relationships based on semantic tags."""
        # Group nodes by semantic tags
        tag_groups = {}
        for filepath, node in self.nodes.items():
            for tag in node.semantic_tags:
                if tag not in tag_groups:
                    tag_groups[tag] = []
                tag_groups[tag].append(filepath)
        
        # Create edges between semantically related nodes
        for tag, filepaths in tag_groups.items():
            if len(filepaths) > 1:
                # Create a semantic cluster
                for i, source in enumerate(filepaths):
                    for target in filepaths[i+1:i+2]:  # Only connect to next node to avoid too many edges
                        edge = GraphEdge(
                            source=source,
                            target=target,
                            relationship_type='semantic_related',
                            metadata={'tag': tag}
                        )
                        self.edges.append(edge)
    
    def _create_type_relationships(self):
        """Create relationships based on component types."""
        # Group nodes by type
        type_groups = {}
        for filepath, node in self.nodes.items():
            if node.type not in type_groups:
                type_groups[node.type] = []
            type_groups[node.type].append(filepath)
        
        # Create special relationships
        agents = type_groups.get('agent', [])
        tools = type_groups.get('tool', [])
        services = type_groups.get('service', [])
        
        # Agents use tools
        for agent in agents:
            for tool in tools[:3]:  # Limit connections
                if 'tool' in self.nodes[agent].semantic_tags:
                    edge = GraphEdge(
                        source=agent,
                        target=tool,
                        relationship_type='uses',
                        metadata={'reason': 'agent_tool_usage'}
                    )
                    self.edges.append(edge)
    
    def _build_graph_structure(self) -> Dict[str, Any]:
        """Build the final graph structure."""
        return {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [edge.to_dict() for edge in self.edges],
            'metadata': {
                'project': str(self.project_path.absolute()),
                'timestamp': datetime.now().isoformat(),
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'languages': list(set(n.language for n in self.nodes.values())),
                'component_types': list(set(n.type for n in self.nodes.values())),
                'semantic_tags': list(set(tag for n in self.nodes.values() for tag in n.semantic_tags))
            },
            'statistics': self._calculate_statistics()
        }
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate graph statistics."""
        # Calculate in/out degrees
        in_degree = {}
        out_degree = {}
        
        for edge in self.edges:
            out_degree[edge.source] = out_degree.get(edge.source, 0) + 1
            in_degree[edge.target] = in_degree.get(edge.target, 0) + 1
        
        # Find most connected nodes
        most_imported = sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:5]
        most_importing = sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Find isolated nodes
        isolated = [f for f in self.nodes if f not in in_degree and f not in out_degree]
        
        return {
            'most_imported': most_imported,
            'most_importing': most_importing,
            'isolated_nodes': isolated,
            'avg_connections': (len(self.edges) * 2) / len(self.nodes) if self.nodes else 0,
            'connectivity': len([n for n in self.nodes if n in in_degree or n in out_degree]) / len(self.nodes) if self.nodes else 0
        }


class GraphDatabase:
    """Simple graph database for querying."""
    
    def __init__(self, graph: Dict[str, Any]):
        self.graph = graph
        self.nodes = {n['filepath']: n for n in graph['nodes']}
        self.edges = graph['edges']
    
    def find_dependencies(self, filepath: str) -> List[str]:
        """Find all dependencies of a file."""
        deps = []
        for edge in self.edges:
            if edge['source'] == filepath and edge['type'] in ('imports', 'depends_on'):
                deps.append(edge['target'])
        return deps
    
    def find_dependents(self, filepath: str) -> List[str]:
        """Find all files that depend on this file."""
        deps = []
        for edge in self.edges:
            if edge['target'] == filepath and edge['type'] in ('imports', 'depends_on'):
                deps.append(edge['source'])
        return deps
    
    def find_by_type(self, component_type: str) -> List[str]:
        """Find all nodes of a specific type."""
        return [f for f, n in self.nodes.items() if n['type'] == component_type]
    
    def find_by_tag(self, tag: str) -> List[str]:
        """Find all nodes with a specific semantic tag."""
        return [f for f, n in self.nodes.items() if tag in n.get('semantic_tags', [])]