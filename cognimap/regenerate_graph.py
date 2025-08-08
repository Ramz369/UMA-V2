#!/usr/bin/env python3
"""
Regenerate the architecture graph with REAL CogniMap components
"""

import json
import os
from pathlib import Path
from datetime import datetime
import hashlib
import ast

def scan_python_file(filepath):
    """Extract metadata from a Python file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse AST to get classes and functions
    try:
        tree = ast.parse(content)
        
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        # Get imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        
        return {
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'size': len(content),
            'lines': content.count('\n')
        }
    except:
        return {
            'classes': [],
            'functions': [],
            'imports': [],
            'size': len(content),
            'lines': content.count('\n')
        }

def generate_real_graph():
    """Generate graph from actual CogniMap files"""
    root = Path(__file__).parent
    nodes = []
    edges = []
    node_map = {}
    
    # Scan all Python files in CogniMap
    for py_file in root.rglob("*.py"):
        # Skip virtual env, node_modules, and test files
        if any(skip in str(py_file) for skip in ['venv/', 'node_modules/', '__pycache__', '.pyc']):
            continue
        
        relative_path = py_file.relative_to(root)
        file_id = hashlib.md5(str(relative_path).encode()).hexdigest()[:8]
        
        # Extract metadata
        metadata = scan_python_file(py_file)
        
        # Determine component type
        component_type = 'module'
        if 'semantic' in str(relative_path):
            component_type = 'semantic_engine'
        elif 'graph' in str(relative_path):
            component_type = 'graph_engine'
        elif 'visualizer' in str(relative_path):
            component_type = 'visualization'
        elif 'collector' in str(relative_path):
            component_type = 'collector'
        elif 'core' in str(relative_path):
            component_type = 'core'
        elif 'server' in str(relative_path) or 'ai_server' in str(relative_path):
            component_type = 'server'
        
        # Create node
        node = {
            'id': file_id,
            'filepath': str(py_file),
            'name': py_file.stem,
            'label': py_file.stem.replace('_', ' ').title(),
            'type': component_type,
            'language': 'python',
            'group': component_type,
            'size': max(10, min(50, metadata['lines'] / 10)),  # Size based on lines
            'metadata': {
                'classes': metadata['classes'],
                'functions': metadata['functions'][:10],  # Limit to first 10
                'imports': list(set(metadata['imports']))[:10],
                'lines': metadata['lines']
            },
            'semantic_tags': [],
            'fingerprint': {
                'id': file_id,
                'birth': datetime.now().isoformat(),
                'intent': f"{py_file.stem} - {component_type} component",
                'version': '1.0.0',
                'hash': file_id
            }
        }
        
        # Add semantic tags based on content
        if metadata['classes']:
            node['semantic_tags'].append('has_classes')
        if metadata['functions']:
            node['semantic_tags'].append('has_functions')
        if 'test' in str(relative_path).lower():
            node['semantic_tags'].append('testing')
        if 'api' in str(relative_path).lower() or 'server' in str(relative_path).lower():
            node['semantic_tags'].append('api')
        if 'async' in str(metadata['functions']):
            node['semantic_tags'].append('async')
        
        nodes.append(node)
        node_map[str(relative_path)] = file_id
    
    # Create edges based on imports
    for node in nodes:
        source_path = Path(node['filepath'])
        source_id = node['id']
        
        for imp in node['metadata'].get('imports', []):
            # Try to find the target file
            if '.' in imp:
                parts = imp.split('.')
                # Check if it's an internal import
                for other_node in nodes:
                    other_path = Path(other_node['filepath'])
                    if other_path.stem in parts or parts[0] in str(other_path):
                        edges.append({
                            'source': source_id,
                            'target': other_node['id'],
                            'type': 'imports',
                            'weight': 1
                        })
                        break
    
    # Add some logical connections based on component types
    # Connect core components to everything
    core_nodes = [n for n in nodes if n['type'] == 'core']
    for core in core_nodes:
        for other in nodes:
            if other['type'] != 'core' and other['id'] != core['id']:
                edges.append({
                    'source': core['id'],
                    'target': other['id'],
                    'type': 'uses',
                    'weight': 0.5
                })
    
    # Connect semantic engine to graph engine
    semantic_nodes = [n for n in nodes if n['type'] == 'semantic_engine']
    graph_nodes = [n for n in nodes if n['type'] == 'graph_engine']
    for sem in semantic_nodes:
        for graph in graph_nodes:
            edges.append({
                'source': sem['id'],
                'target': graph['id'],
                'type': 'analyzes',
                'weight': 2
            })
    
    # Connect server to all engines
    server_nodes = [n for n in nodes if n['type'] == 'server']
    for server in server_nodes:
        for engine in nodes:
            if 'engine' in engine['type']:
                edges.append({
                    'source': server['id'],
                    'target': engine['id'],
                    'type': 'orchestrates',
                    'weight': 1.5
                })
    
    # Create the graph structure
    graph = {
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'generated': datetime.now().isoformat(),
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'components': {
                'core': len([n for n in nodes if n['type'] == 'core']),
                'semantic_engine': len([n for n in nodes if n['type'] == 'semantic_engine']),
                'graph_engine': len([n for n in nodes if n['type'] == 'graph_engine']),
                'visualization': len([n for n in nodes if n['type'] == 'visualization']),
                'server': len([n for n in nodes if n['type'] == 'server'])
            }
        }
    }
    
    return graph

if __name__ == "__main__":
    print("Regenerating architecture graph with real CogniMap components...")
    
    graph = generate_real_graph()
    
    # Save the new graph
    output_path = Path("visualizer/output/architecture_graph_real.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(graph, f, indent=2)
    
    print(f"✅ Generated real graph with {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
    print(f"   Saved to: {output_path}")
    
    # Show component breakdown
    print("\nComponent breakdown:")
    for comp_type, count in graph['metadata']['components'].items():
        print(f"  - {comp_type}: {count} files")