#!/usr/bin/env python3
"""
Smart Context Builder for AI Analysis
Builds focused, relevant context windows for DeepSeek analysis
instead of sending entire codebase
"""

import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib


class SmartContextBuilder:
    """Build intelligent context windows for AI analysis"""
    
    def __init__(self, max_tokens: int = 4000):
        """
        Initialize with max token limit for context
        DeepSeek performs better with focused 4-8k token contexts
        """
        self.max_tokens = max_tokens
        self.char_to_token_ratio = 4  # Rough estimate: 4 chars = 1 token
        self.max_chars = max_tokens * self.char_to_token_ratio
    
    def build_node_context(self, node_id: str, graph_data: Dict) -> Dict[str, Any]:
        """
        Build focused context for a specific node
        Returns only relevant code and connections
        """
        # Find the target node
        target_node = None
        for node in graph_data['nodes']:
            if node['id'] == node_id:
                target_node = node
                break
        
        if not target_node:
            return {'error': 'Node not found'}
        
        context = {
            'target': target_node,
            'code_snippet': self._get_code_snippet(target_node),
            'direct_dependencies': self._get_dependencies(node_id, graph_data),
            'direct_dependents': self._get_dependents(node_id, graph_data),
            'related_files': self._get_related_files(target_node, graph_data),
            'architectural_context': self._get_architectural_context(target_node)
        }
        
        return context
    
    def _get_code_snippet(self, node: Dict, max_lines: int = 100) -> Optional[str]:
        """Get actual code snippet from file if it exists"""
        filepath = node.get('filepath')
        if not filepath or not Path(filepath).exists():
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # For large files, extract key parts
            if len(lines) > max_lines:
                # Get imports, class definitions, and main functions
                code_parts = []
                
                # Get imports (first 20 lines usually)
                code_parts.append(''.join(lines[:20]))
                code_parts.append('\n# ... [middle section omitted for brevity] ...\n\n')
                
                # Try to get class definitions
                content = ''.join(lines)
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Get class definition and docstring
                        start_line = node.lineno - 1
                        end_line = min(start_line + 30, len(lines))
                        code_parts.append(''.join(lines[start_line:end_line]))
                        code_parts.append('\n    # ... [methods omitted] ...\n\n')
                        break
                
                return ''.join(code_parts)[:self.max_chars // 4]
            else:
                return ''.join(lines)[:self.max_chars // 4]
        except Exception as e:
            return f"# Error reading file: {e}"
    
    def _get_dependencies(self, node_id: str, graph_data: Dict) -> List[Dict]:
        """Get nodes that this node depends on"""
        deps = []
        for edge in graph_data.get('edges', []):
            if edge['source'] == node_id:
                # Find target node
                for node in graph_data['nodes']:
                    if node['id'] == edge['target']:
                        deps.append({
                            'name': node.get('name'),
                            'type': node.get('type'),
                            'filepath': node.get('filepath')
                        })
                        break
        return deps[:10]  # Limit to 10 most important
    
    def _get_dependents(self, node_id: str, graph_data: Dict) -> List[Dict]:
        """Get nodes that depend on this node"""
        deps = []
        for edge in graph_data.get('edges', []):
            if edge['target'] == node_id:
                # Find source node
                for node in graph_data['nodes']:
                    if node['id'] == edge['source']:
                        deps.append({
                            'name': node.get('name'),
                            'type': node.get('type'),
                            'filepath': node.get('filepath')
                        })
                        break
        return deps[:10]  # Limit to 10 most important
    
    def _get_related_files(self, target_node: Dict, graph_data: Dict) -> List[Dict]:
        """Get files in same directory or module"""
        related = []
        target_path = Path(target_node.get('filepath', ''))
        target_dir = target_path.parent
        
        for node in graph_data['nodes']:
            node_path = Path(node.get('filepath', ''))
            if node_path.parent == target_dir and node['id'] != target_node['id']:
                related.append({
                    'name': node.get('name'),
                    'type': node.get('type')
                })
        
        return related[:5]
    
    def _get_architectural_context(self, node: Dict) -> Dict:
        """Provide high-level architectural context"""
        filepath = Path(node.get('filepath', ''))
        
        # Determine layer/component type from path
        path_str = str(filepath).lower()
        
        if 'semantic' in path_str:
            return {
                'layer': 'Semantic Analysis',
                'purpose': 'Analyzes code semantics, patterns, and relationships',
                'key_responsibilities': [
                    'Symbol extraction and analysis',
                    'Pattern detection',
                    'Semantic fingerprinting'
                ]
            }
        elif 'graph' in path_str:
            return {
                'layer': 'Graph Engine',
                'purpose': 'Builds and analyzes architectural graphs',
                'key_responsibilities': [
                    'Graph construction from code',
                    'Relationship mapping',
                    'Complexity analysis'
                ]
            }
        elif 'visualizer' in path_str:
            return {
                'layer': 'Visualization',
                'purpose': 'Interactive visualization of architecture',
                'key_responsibilities': [
                    'Graph rendering',
                    'User interaction',
                    'Visual analytics'
                ]
            }
        elif 'core' in path_str:
            return {
                'layer': 'Core Framework',
                'purpose': 'Foundation components and protocols',
                'key_responsibilities': [
                    'Base abstractions',
                    'Common utilities',
                    'Protocol definitions'
                ]
            }
        else:
            return {
                'layer': 'Application',
                'purpose': 'Application-level functionality',
                'key_responsibilities': ['Component-specific logic']
            }
    
    def build_gap_analysis_context(self, graph_data: Dict) -> Dict:
        """Build context specifically for gap analysis"""
        # Focus on architectural overview rather than full code
        context = {
            'total_components': len(graph_data.get('nodes', [])),
            'total_connections': len(graph_data.get('edges', [])),
            'component_types': {},
            'orphaned_components': [],
            'highly_coupled': [],
            'missing_tests': [],
            'architectural_layers': {}
        }
        
        # Analyze component distribution
        for node in graph_data.get('nodes', []):
            comp_type = node.get('type', 'unknown')
            if comp_type not in context['component_types']:
                context['component_types'][comp_type] = []
            context['component_types'][comp_type].append(node.get('name'))
        
        # Find orphaned components (no connections)
        connected_nodes = set()
        for edge in graph_data.get('edges', []):
            connected_nodes.add(edge['source'])
            connected_nodes.add(edge['target'])
        
        for node in graph_data.get('nodes', []):
            if node['id'] not in connected_nodes:
                context['orphaned_components'].append({
                    'name': node.get('name'),
                    'type': node.get('type'),
                    'filepath': node.get('filepath')
                })
        
        # Find highly coupled components (>10 connections)
        connection_count = {}
        for edge in graph_data.get('edges', []):
            connection_count[edge['source']] = connection_count.get(edge['source'], 0) + 1
            connection_count[edge['target']] = connection_count.get(edge['target'], 0) + 1
        
        for node_id, count in connection_count.items():
            if count > 10:
                for node in graph_data['nodes']:
                    if node['id'] == node_id:
                        context['highly_coupled'].append({
                            'name': node.get('name'),
                            'connections': count
                        })
                        break
        
        # Check for missing tests
        all_files = set(node.get('name') for node in graph_data['nodes'])
        test_files = set(node.get('name') for node in graph_data['nodes'] 
                         if 'test' in node.get('name', '').lower())
        
        for node in graph_data['nodes']:
            name = node.get('name', '')
            if not name.startswith('test_') and f"test_{name}" not in test_files:
                context['missing_tests'].append(name)
        
        return context
    
    def create_focused_prompt(self, context: Dict, analysis_type: str = 'node') -> str:
        """Create a focused prompt for DeepSeek with relevant context"""
        if analysis_type == 'node':
            node = context.get('target', {})
            code = context.get('code_snippet', 'No code available')
            
            prompt = f"""
Analyze this specific component from CogniMap architecture:

Component: {node.get('name')}
Type: {node.get('type')}
File: {node.get('filepath')}

Architectural Context:
{json.dumps(context.get('architectural_context', {}), indent=2)}

Code Snippet (truncated):
```python
{code[:2000] if code else 'No code available'}
```

Direct Dependencies ({len(context.get('direct_dependencies', []))}):
{json.dumps(context.get('direct_dependencies', [])[:5], indent=2)}

Direct Dependents ({len(context.get('direct_dependents', []))}):
{json.dumps(context.get('direct_dependents', [])[:5], indent=2)}

Related Files in Module:
{json.dumps(context.get('related_files', []), indent=2)}

Please provide:
1. Specific purpose of this component in CogniMap
2. Code quality issues (if visible in snippet)
3. Missing error handling or edge cases
4. Suggestions for better integration with {node.get('type')} components
5. Security or performance concerns specific to this code

Focus on actionable, specific feedback based on the actual code shown.
"""
        
        elif analysis_type == 'gap':
            prompt = f"""
Analyze architectural gaps in CogniMap system:

System Overview:
- Total Components: {context.get('total_components')}
- Total Connections: {context.get('total_connections')}

Component Distribution:
{json.dumps(context.get('component_types', {}), indent=2)}

Orphaned Components (no connections):
{json.dumps(context.get('orphaned_components', [])[:10], indent=2)}

Highly Coupled Components:
{json.dumps(context.get('highly_coupled', [])[:10], indent=2)}

Components Missing Tests:
{json.dumps(context.get('missing_tests', [])[:20], indent=2)}

Identify:
1. Missing architectural components (what's needed but not present)
2. Integration gaps between existing components
3. Missing abstractions or interfaces
4. Architectural anti-patterns visible in structure
5. Priority improvements for system robustness

Be specific about WHAT is missing and WHERE it should be added.
"""
        
        return prompt


def enhanced_deepseek_request(node_id: str, graph_path: Path, api_key: str) -> Dict:
    """
    Make an enhanced DeepSeek request with focused context
    """
    import requests
    
    # Load graph data
    with open(graph_path, 'r') as f:
        graph_data = json.load(f)
    
    # Build focused context
    builder = SmartContextBuilder(max_tokens=4000)
    context = builder.build_node_context(node_id, graph_data)
    
    # Create focused prompt
    prompt = builder.create_focused_prompt(context, 'node')
    
    # Make DeepSeek request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "You are analyzing CogniMap, a living architecture visualization system. Provide specific, actionable feedback based on the actual code provided."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,  # Lower temperature for more focused analysis
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return {
            'success': True,
            'analysis': data['choices'][0]['message']['content'],
            'context_size': len(prompt),
            'focused': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'context_size': len(prompt)
        }


if __name__ == "__main__":
    # Test the smart context builder
    builder = SmartContextBuilder()
    
    # Load sample graph
    graph_path = Path("visualizer/output/architecture_graph_enhanced.json")
    if graph_path.exists():
        with open(graph_path, 'r') as f:
            graph_data = json.load(f)
        
        # Test with first node
        if graph_data['nodes']:
            node_id = graph_data['nodes'][0]['id']
            context = builder.build_node_context(node_id, graph_data)
            
            print("Built context for node:", context.get('target', {}).get('name'))
            print("Context includes:")
            print(f"  - Code snippet: {len(context.get('code_snippet', '')) if context.get('code_snippet') else 0} chars")
            print(f"  - Dependencies: {len(context.get('direct_dependencies', []))}")
            print(f"  - Dependents: {len(context.get('direct_dependents', []))}")
            
            # Test gap analysis context
            gap_context = builder.build_gap_analysis_context(graph_data)
            print("\nGap analysis context:")
            print(f"  - Orphaned components: {len(gap_context['orphaned_components'])}")
            print(f"  - Highly coupled: {len(gap_context['highly_coupled'])}")
            print(f"  - Missing tests: {len(gap_context['missing_tests'])}")