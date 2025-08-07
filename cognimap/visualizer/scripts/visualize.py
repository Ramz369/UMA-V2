#!/usr/bin/env python3
"""
Interactive CogniMap Visualization Tool
Run this to explore your codebase architecture visually
"""

from cognimap.graph.graph_builder import GraphBuilder
from cognimap.graph.graph_visualizer import GraphVisualizer
from cognimap.graph.graph_analyzer import GraphAnalyzer
import json
from pathlib import Path

def main():
    print("=" * 80)
    print("🧠 COGNIMAP ARCHITECTURE VISUALIZATION")
    print("=" * 80)
    
    # Build the graph
    print("\n📊 Building architecture graph...")
    builder = GraphBuilder()
    graph = builder.build()
    
    print(f"\n✅ Graph Statistics:")
    print(f"   • Components: {len(graph['nodes'])}")
    print(f"   • Relationships: {len(graph['edges'])}")
    
    # Analyze the architecture
    print("\n🔍 Analyzing architecture...")
    analyzer = GraphAnalyzer(graph)
    analysis = analyzer.analyze()
    
    print(f"\n📈 Architecture Analysis:")
    print(f"   • Circular Dependencies: {len(analysis['circular_dependencies'])}")
    print(f"   • Highly Coupled Components: {len(analysis['coupling_analysis']['highly_coupled'])}")
    print(f"   • Isolated Components: {len(analysis['isolated_components'])}")
    print(f"   • Hub Components: {len(analysis['hub_components'])}")
    
    # Create visualizations
    visualizer = GraphVisualizer(graph)
    
    # 1. Text Visualization
    print("\n" + "=" * 80)
    print("📝 TEXT VISUALIZATION (Top Components)")
    print("=" * 80)
    text_viz = visualizer.create_text_visualization()
    lines = text_viz.split('\n')[:30]  # Show first 30 lines
    print('\n'.join(lines))
    
    # 2. Dependency Tree
    print("\n" + "=" * 80)
    print("🌳 DEPENDENCY TREE (from cognimap/cli.py)")
    print("=" * 80)
    tree_viz = visualizer.create_dependency_tree("cognimap/cli.py")
    lines = tree_viz.split('\n')[:40]  # Show first 40 lines
    print('\n'.join(lines))
    
    # 3. Save Mermaid Diagram
    print("\n" + "=" * 80)
    print("🎨 MERMAID DIAGRAM")
    print("=" * 80)
    mermaid = visualizer.create_mermaid_diagram()
    
    # Save to file
    with open('cognimap_architecture.mmd', 'w') as f:
        f.write(mermaid)
    print("✅ Mermaid diagram saved to: cognimap_architecture.mmd")
    print("   View online at: https://mermaid.live/")
    
    # 4. Save full analysis to JSON
    with open('cognimap_analysis.json', 'w') as f:
        json.dump({
            'statistics': {
                'total_nodes': len(graph['nodes']),
                'total_edges': len(graph['edges']),
                'node_types': {}
            },
            'analysis': analysis,
            'top_components': graph['nodes'][:10] if 'nodes' in graph else []
        }, f, indent=2, default=str)
    print("✅ Full analysis saved to: cognimap_analysis.json")
    
    # 5. Interactive exploration options
    print("\n" + "=" * 80)
    print("🚀 INTERACTIVE EXPLORATION OPTIONS")
    print("=" * 80)
    print("\n1. View Mermaid diagram online:")
    print("   • Copy contents of cognimap_architecture.mmd")
    print("   • Go to https://mermaid.live/")
    print("   • Paste and see interactive diagram")
    
    print("\n2. Explore specific components:")
    print("   python3 -c \"from cognimap.graph.graph_builder import GraphBuilder; builder = GraphBuilder(scope='cognimap'); print(builder.build())\"")
    
    print("\n3. Search by semantic tags:")
    components_by_tag = {}
    for node in graph['nodes']:
        if 'semantic_tags' in node:
            for tag in node['semantic_tags']:
                if tag not in components_by_tag:
                    components_by_tag[tag] = []
                components_by_tag[tag].append(node['filepath'])
    
    print("\n   Available semantic tags:")
    for tag, files in list(components_by_tag.items())[:10]:
        print(f"   • {tag}: {len(files)} components")
    
    print("\n4. Component type distribution:")
    type_dist = {}
    for node in graph['nodes']:
        node_type = node.get('type', 'unknown')
        type_dist[node_type] = type_dist.get(node_type, 0) + 1
    
    for node_type, count in sorted(type_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {node_type}: {count} components")
    
    print("\n" + "=" * 80)
    print("✨ CogniMap visualization complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()