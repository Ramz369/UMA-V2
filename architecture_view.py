#!/usr/bin/env python3
"""
Create a clean architecture visualization of COGPLAN.
"""

from cognimap.graph.graph_builder import GraphBuilder
from pathlib import Path


def create_clean_visualization():
    """Create a clean, focused architecture visualization."""
    
    # Build graph
    print("Building architecture graph...")
    builder = GraphBuilder('.')
    graph = builder.build()
    
    nodes = {n['filepath']: n for n in graph['nodes']}
    edges = graph['edges']
    
    # Group by major components
    architecture = {
        'Core Agents': [],
        'Evolution System': [],
        'Tools Ecosystem': [],
        'Testing': [],
        'Infrastructure': []
    }
    
    for filepath, node in nodes.items():
        name = Path(filepath).stem
        
        if 'src/agents' in filepath:
            architecture['Core Agents'].append((name, filepath, node))
        elif 'evolution' in filepath:
            architecture['Evolution System'].append((name, filepath, node))
        elif 'tools' in filepath and 'test' not in filepath:
            architecture['Tools Ecosystem'].append((name, filepath, node))
        elif 'test' in filepath:
            architecture['Testing'].append((name, filepath, node))
        elif any(x in filepath for x in ['semloop', 'services', 'scripts']):
            architecture['Infrastructure'].append((name, filepath, node))
    
    # Print clean visualization
    print("\n" + "=" * 80)
    print(" " * 25 + "🏗️  COGPLAN ARCHITECTURE")
    print("=" * 80)
    
    # Show main component flow
    print("\n📊 COMPONENT FLOW:")
    print("─" * 60)
    print("""
    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │   PLANNER   │────▶│   CODEGEN   │────▶│    TOOLS    │
    │    AGENT    │     │    AGENT    │     │   HUNTER    │
    └─────────────┘     └─────────────┘     └─────────────┘
           │                   │                    │
           ▼                   ▼                    ▼
    ┌─────────────────────────────────────────────────────┐
    │                  TOOLS ECOSYSTEM                     │
    │  ├─ Foundation (filesystem, code_executor)          │
    │  ├─ Intelligence (web_search, vector_search)        │
    │  └─ Evolution (data_connector, github, slack)       │
    └─────────────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────┐
    │                 EVOLUTION FRAMEWORK                  │
    │  ├─ Aether (consciousness substrate)                │
    │  ├─ Agents (architect, reviewer, auditor)           │
    │  └─ Treasury (crypto wallet integration)            │
    └─────────────────────────────────────────────────────┘
    """)
    
    # Show detailed components
    for category, components in architecture.items():
        if not components:
            continue
            
        print(f"\n📦 {category.upper()} ({len(components)} components)")
        print("─" * 60)
        
        # Sort by importance (based on connections)
        components_with_score = []
        for name, filepath, node in components[:10]:  # Limit to top 10
            imports = len([e for e in edges if e['source'] == filepath])
            imported_by = len([e for e in edges if e['target'] == filepath])
            score = imports + imported_by * 2  # Weight being imported higher
            components_with_score.append((name, filepath, node, score))
        
        components_with_score.sort(key=lambda x: x[3], reverse=True)
        
        for name, filepath, node, score in components_with_score[:5]:  # Show top 5
            tags = node.get('semantic_tags', [])[:3]
            print(f"  • {name}")
            if tags:
                print(f"    Tags: {', '.join(tags)}")
            if score > 0:
                print(f"    Importance: {'★' * min(5, score // 4)}")
    
    # Show relationships summary
    print("\n🔗 KEY RELATIONSHIPS:")
    print("─" * 60)
    
    # Find most important connections
    connection_counts = {}
    for edge in edges:
        if edge['type'] == 'imports':
            pair = (Path(edge['source']).stem, Path(edge['target']).stem)
            if pair[0] != pair[1]:  # Skip self-references
                connection_counts[pair] = connection_counts.get(pair, 0) + 1
    
    # Show top connections
    top_connections = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for (source, target), count in top_connections:
        if count > 1:
            print(f"  {source} ──→ {target}")
    
    # Show statistics
    stats = graph.get('statistics', {})
    print("\n📈 ARCHITECTURE METRICS:")
    print("─" * 60)
    print(f"  Total Components: {graph['metadata']['node_count']}")
    print(f"  Total Relationships: {graph['metadata']['edge_count']}")
    print(f"  Connectivity: {stats.get('connectivity', 0):.1%}")
    print(f"  Average Connections: {stats.get('avg_connections', 0):.1f}")
    
    # Show health status
    print("\n🏥 HEALTH STATUS:")
    print("─" * 60)
    
    # Check various health metrics
    test_ratio = len([n for n in nodes if 'test' in n]) / len(nodes)
    isolated = stats.get('isolated_nodes', [])
    
    if test_ratio > 0.3:
        print(f"  ✅ Good test coverage ({test_ratio:.1%})")
    else:
        print(f"  ⚠️  Low test coverage ({test_ratio:.1%})")
    
    if len(isolated) < 5:
        print(f"  ✅ Few isolated components ({len(isolated)})")
    else:
        print(f"  ⚠️  Many isolated components ({len(isolated)})")
    
    if stats.get('connectivity', 0) > 0.9:
        print(f"  ✅ High connectivity ({stats.get('connectivity', 0):.1%})")
    else:
        print(f"  ⚠️  Low connectivity ({stats.get('connectivity', 0):.1%})")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    create_clean_visualization()